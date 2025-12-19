-- ======================================================================================================================
-- FUNCTION: get_tax_optimized
--
-- PURPOSE:
--   Calcula un resumen detallado de las bases imponibles e impuestos asociados a un asiento contable específico
--   ('account.move'), basado en las líneas contables etiquetadas ('account.move.line') y sus relaciones con
--   etiquetas fiscales ('account.account.tag').
--
-- DESCRIPCIÓN GENERAL:
--   1. Selecciona las líneas del asiento que no están canceladas.
--   2. Ajusta el signo de los saldos ('balance') según el tipo de movimiento (p_move_type) para normalizar los importes.
--   3. Asocia las líneas con sus etiquetas fiscales y normaliza los nombres de dichas etiquetas para análisis coherente.
--   4. Agrega los montos ajustados en categorías fiscales predefinidas basadas en el nombre normalizado de la etiqueta.
--   5. Devuelve una tupla con los montos agrupados por categoría, redondeados a dos decimales.
--
-- PARÁMETROS:
--   p_account_move_id           INTEGER  → ID del asiento contable ('account.move.id') a analizar.
--   p_move_type                 VARCHAR  → Tipo de movimiento ('out_invoice', 'in_invoice', etc.), afecta el signo del balance.
--   p_l10n_document_type_code   VARCHAR  → Código del tipo de documento (localización). Actualmente no se utiliza.
--
-- RETORNO:
--   RECORD (tupla anónima con 13 campos NUMERIC, redondeados a 2 decimales).
--   El orden de los campos es ESTRICTAMENTE relevante para su interpretación posterior.
--
--   CAMPOS DEVUELTOS (en orden):
--     1.  base_exported_amount           → Base Imponible de Operaciones de Exportación (S_BASE_EXP)
--     2.  base_taxable_general_amount    → Base Imponible de Operaciones Gravadas Generales (S_BASE_OG)
--     3.  base_taxable_discount_amount   → Base Imponible con Descuento (S_BASE_OGD)
--     4.  tax_vat_general_amount         → IGV/IVA por Operaciones Gravadas Generales (S_TAX_OG)
--     5.  tax_vat_discount_amount        → IGV/IVA por Descuentos Otorgados (S_TAX_OGD)
--     6.  base_exempt_amount             → Base Imponible Exonerada (S_BASE_OE)
--     7.  base_unaffected_amount         → Base Imponible Inafecta (S_BASE_OU)
--     8.  tax_excise_amount              → ISC - Impuesto Selectivo al Consumo (S_TAX_ISC)
--     9.  tax_plastic_bag_amount         → ICBPER - Impuesto a Bolsas de Plástico (S_TAX_ICBP)
--    10.  base_rice_paddy_tax_amount     → Base Imponible IVAP - Arroz Pilado (S_BASE_IVAP)
--    11.  tax_rice_paddy_tax_amount      → Monto del Impuesto IVAP (S_TAX_IVAP)
--    12.  tax_other_amount               → Otros Tributos y Cargos (S_TAX_OTHER)
--    13.  total_tagged_lines_amount      → Total general de montos ajustados de líneas con etiquetas fiscales.
-- ======================================================================================================================
CREATE OR REPLACE FUNCTION get_tax_optimized(
    p_account_move_id           INTEGER,  -- ID del asiento contable (account.move.id)
    p_move_type                 VARCHAR,  -- Tipo de movimiento: 'out_invoice', 'in_invoice', etc.
    p_l10n_document_type_code   VARCHAR   -- Código del tipo de documento (opcional, según necesidad)
)
RETURNS RECORD
LANGUAGE plpgsql
AS $$
DECLARE
    -- 📌 Resultado final: tupla que contiene los montos agregados y normalizados
    v_result_tuple RECORD;

    -- 📊 Montos base y de impuestos, agrupados por tipo de etiqueta fiscal
    v_base_exported_amount          NUMERIC := 0.0;
    v_base_taxable_general_amount   NUMERIC := 0.0;
    v_base_taxable_discount_amount  NUMERIC := 0.0;
    v_tax_vat_general_amount        NUMERIC := 0.0;
    v_tax_vat_discount_amount       NUMERIC := 0.0;
    v_base_exempt_amount            NUMERIC := 0.0;
    v_base_unaffected_amount        NUMERIC := 0.0;
    v_tax_excise_amount             NUMERIC := 0.0;
    v_tax_plastic_bag_amount        NUMERIC := 0.0;
    v_base_rice_paddy_tax_amount    NUMERIC := 0.0;
    v_tax_rice_paddy_tax_amount     NUMERIC := 0.0;
    v_tax_other_amount              NUMERIC := 0.0;

    -- 📈 Total acumulado de todas las líneas etiquetadas
    -- v_total_tagged_lines_amount     NUMERIC := 0.0;
BEGIN
    -- CTE (Common Table Expression) 'RelevantMoveLines':
    -- Extrae líneas relevantes del asiento contable especificado (account_move_line),
    -- ajustando el signo del balance según el tipo de documento para normalizar valores en reportes fiscales.
    WITH RelevantMoveLines AS (
        SELECT
            -- ID de la línea contable
            aml.id AS line_id,
            -- Balance original de la línea, necesario para el CASE siguiente
            aml.balance,
            -- Ajustar el signo del balance para documentos de cliente (ventas).
            CASE
                WHEN p_move_type IN ('out_invoice', 'out_refund')
                    THEN -aml.balance
                ELSE aml.balance
            END AS adjusted_line_amount
        FROM account_move_line aml
        WHERE aml.move_id = p_account_move_id
        AND aml.parent_state != 'cancel' -- Excluir líneas de asientos cancelados
    ),

    -- CTE 'LineTaxTags':
    -- Une líneas contables con sus etiquetas fiscales y normaliza el nombre de la etiqueta para comparación.
    LineTaxTags AS (
        SELECT
            -- Monto ajustado de la línea
            rml.adjusted_line_amount,
            -- Nombre de etiqueta fiscal, traducido y limpiado
            REPLACE(
                REPLACE(
                    CASE 
                        -- Verifica si el campo 'name' es un objeto JSON (empieza: '{', termina: '}').
                        -- Esto detecta si el contenido es un JSON multilingüe
                        WHEN aat.name::text LIKE '{%}' THEN
                            COALESCE(
                                -- Intenta obtener el valor de la clave 'en_US'
                                aat.name::jsonb ->> 'en_US',
                                -- Si 'en_US' no está o es null, intenta con 'es_PE'
                                aat.name::jsonb ->> 'es_PE',
                                -- Si ninguna de las claves existe, retorna NULL
                                NULL
                            )
                        ELSE
                            -- Si no es JSON, usa el nombre directamente.
                            TRIM(BOTH '"' FROM aat.name)
                    END,
                '-', ''),   -- Limpieza de guiones
            '+', '')        -- Limpieza de signos más
            AS normalized_tag_name
        FROM RelevantMoveLines rml
        JOIN account_account_tag_account_move_line_rel      tax_rel     ON tax_rel.account_move_line_id = rml.line_id
        JOIN account_account_tag                            aat         ON tax_rel.account_account_tag_id = aat.id
    )

    -- Consulta principal de agregación:
    -- Suma por cada etiqueta fiscal normalizada (basado en LineTaxTags).
    SELECT
        COALESCE(SUM(CASE WHEN ltt.normalized_tag_name = 'S_BASE_EXP'   THEN ltt.adjusted_line_amount ELSE 0 END), 0.0), -- base_exported
        COALESCE(SUM(CASE WHEN ltt.normalized_tag_name = 'S_BASE_OG'    THEN ltt.adjusted_line_amount ELSE 0 END), 0.0), -- base_taxable_general
        COALESCE(SUM(CASE WHEN ltt.normalized_tag_name = 'S_BASE_OGD'   THEN ltt.adjusted_line_amount ELSE 0 END), 0.0), -- base_taxable_discount
        COALESCE(SUM(CASE WHEN ltt.normalized_tag_name = 'S_TAX_OG'     THEN ltt.adjusted_line_amount ELSE 0 END), 0.0), -- tax_vat_general
        COALESCE(SUM(CASE WHEN ltt.normalized_tag_name = 'S_TAX_OGD'    THEN ltt.adjusted_line_amount ELSE 0 END), 0.0), -- tax_vat_discount
        COALESCE(SUM(CASE WHEN ltt.normalized_tag_name = 'S_BASE_OE'    THEN ltt.adjusted_line_amount ELSE 0 END), 0.0), -- base_exempt
        COALESCE(SUM(CASE WHEN ltt.normalized_tag_name = 'S_BASE_OU'    THEN ltt.adjusted_line_amount ELSE 0 END), 0.0), -- base_unaffected
        COALESCE(SUM(CASE WHEN ltt.normalized_tag_name = 'S_TAX_ISC'    THEN ltt.adjusted_line_amount ELSE 0 END), 0.0), -- tax_excise
        COALESCE(SUM(CASE WHEN ltt.normalized_tag_name = 'S_TAX_ICBP'   THEN ltt.adjusted_line_amount ELSE 0 END), 0.0), -- tax_plastic_bag
        COALESCE(SUM(CASE WHEN ltt.normalized_tag_name = 'S_BASE_IVAP'  THEN ltt.adjusted_line_amount ELSE 0 END), 0.0), -- base_rice_paddy
        COALESCE(SUM(CASE WHEN ltt.normalized_tag_name = 'S_TAX_IVAP'   THEN ltt.adjusted_line_amount ELSE 0 END), 0.0), -- tax_rice_paddy
        COALESCE(SUM(CASE WHEN ltt.normalized_tag_name = 'S_TAX_OTHER'  THEN ltt.adjusted_line_amount ELSE 0 END), 0.0) -- tax_other
        -- COALESCE(SUM(ltt.adjusted_line_amount), 0.0) -- total_tagged_lines
    INTO
        v_base_exported_amount,
        v_base_taxable_general_amount,
        v_base_taxable_discount_amount,
        v_tax_vat_general_amount,
        v_tax_vat_discount_amount,
        v_base_exempt_amount,
        v_base_unaffected_amount,
        v_tax_excise_amount,
        v_tax_plastic_bag_amount,
        v_base_rice_paddy_tax_amount,
        v_tax_rice_paddy_tax_amount,
        v_tax_other_amount
        -- v_total_tagged_lines_amount
    FROM LineTaxTags ltt;

    -- 📌 Construcción del registro final (v_result_tuple) que será devuelto por la función.
    v_result_tuple := (
        ROUND(v_base_exported_amount,           2),
        ROUND(v_base_taxable_general_amount,    2),
        ROUND(v_base_taxable_discount_amount,   2),
        ROUND(v_tax_vat_general_amount,         2),
        ROUND(v_tax_vat_discount_amount,        2),
        ROUND(v_base_exempt_amount,             2),
        ROUND(v_base_unaffected_amount,         2),
        ROUND(v_tax_excise_amount,              2),
        ROUND(v_tax_plastic_bag_amount,         2),
        ROUND(v_base_rice_paddy_tax_amount,     2),
        ROUND(v_tax_rice_paddy_tax_amount,      2),
        ROUND(v_tax_other_amount,               2)
        -- ROUND(v_total_tagged_lines_amount,      2),
    );

    RETURN v_result_tuple;
END;
$$;