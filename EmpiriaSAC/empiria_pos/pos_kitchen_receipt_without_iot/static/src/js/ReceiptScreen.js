odoo.define('pos_kitchen_receipt_without_iot.KitchenReceiptScreen', function (require) {
    'use strict';

    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
    const Registries = require('point_of_sale.Registries');
    const { useErrorHandlers } = require('point_of_sale.custom_hooks');
    const { onMounted } = owl;

    const KitchenReceiptScreen = (ReceiptScreen) => {
        class KitchenReceiptScreen extends ReceiptScreen {
            setup() {
                // super.setup();
                useErrorHandlers();
                this.report = this.props.report.normal;
                this.reportList = this.props.report.list;
                this.len = this.props.report.list.length;
                this.config = this.env.pos.config;

                onMounted(() => {
                    this.create_html_receipts();
                    setTimeout(async () => {
                        await this.handleAutoPrint();
                    }, 0);
                });
            }
            create_html_receipts(){
                let data_receipt = $('#data-receipt')
                if (this.config.use_multi_printer) {
                    for (let index = 0; index < this.reportList.length; index++) {
                        let rep = this.reportList[index];
                        this.create_button_receipt(index, rep)
                    }
                } else {
                    this.create_button_receipt(0, this.report)
                }
            }

            create_button_receipt(index, data_html){
                let self = this;
                let data_receipt = $('#data-receipt')

                // Crear el elemento botón
                let button = $("<div>").addClass("button print");
                button.on("click", async function() {
                    await self.printReceipt(index)

                });

                // Crear el icono dentro del botón
                let icon = $("<i>").addClass("fa fa-print");
                button.append(icon);

                // Agregar el texto "Print" dentro del botón
                let buttonText = $("<span>").text(this.env._t("Print"));
                button.append(buttonText);

                // Crear el elemento contenedor de ticket
                let container = $("<div>").addClass("pos-receipt-container").attr("id", `ticket_container_${index}`);

                // Agregar el contenido del reporte dentro del contenedor
                container.html(data_html);

                // Agregar el botón y el contenedor al DOM
                data_receipt.append(button);
                data_receipt.append(container);
            }

            confirm() {
                this.props.resolve({confirmed: true, payload: null});
                this.trigger('close-temp-screen');
            }

            async printReceipt(index) {
                if (!this.config.use_multi_printer) {
                    await this._default_print();
                } else {
                    await this._print_by_ticket(index);
                }
            }

            async _default_print() {
                const isPrinted = await this._printReceipt();
                if (isPrinted && !this.env.pos.config.allow_kitchens_receipt) {
                    this.currentOrder._printed = true;
                }
            }

            async _print_by_ticket(index) {
                const printOptions = {
                    printable: 'ticket_container_' + index,
                    type: 'html',
                    targetStyles: ['*'],
                    css: '/web/assets/*.css',
                    scanStyles: true,
                    showModal: false,
                    documentTitle: "",
                    honorMarginPadding: false
                };
            
                if (this.env.proxy.printer) {
                    let html_data = $(`#ticket_container_${index}`).html();
                    const printResult = await this.env.proxy.printer.print_receipt(html_data);
                    if (printResult.successful) {
                        return true;
                    } else {
                        await this.showPopup('ErrorPopup', {
                            title: printResult.message.title,
                            body: printResult.message.body,
                        });
                        const { confirmed } = await this.showPopup('ConfirmPopup', {
                            title: printResult.message.title,
                            body: 'Do you want to print using the web printer?',
                        });
                        if (confirmed) {
                            try {
                                printJS(printOptions);
                            } catch (err) {
                                await this.showPopup('ErrorPopup', {
                                    title: this.env._t('Printing is not supported on some browsers'),
                                    body: this.env._t(
                                        'Printing is not supported on some browsers due to no default printing protocol ' +
                                            'is available. It is possible to print your tickets by making use of an IoT Box.'
                                    ),
                                });
                            }
                        }
                        return false;
                    }
                } else {
                    try {
                        printJS(printOptions);
                    } catch (err) {
                        await this.showPopup('ErrorPopup', {
                            title: this.env._t('Printing is not supported on some browsers'),
                            body: this.env._t(
                                'Printing is not supported on some browsers due to no default printing protocol ' +
                                    'is available. It is possible to print your tickets by making use of an IoT Box.'
                            ),
                        });
                    }
                }
            }
        }

        KitchenReceiptScreen.template = 'KitchenReceiptScreen';
        return KitchenReceiptScreen;
    };

    Registries.Component.addByExtending(KitchenReceiptScreen, ReceiptScreen);

    return KitchenReceiptScreen;
});
