/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { BenefitUnitWidget } from "@g2p_pbms/js/benefit_unit_widget";

patch(BenefitUnitWidget.prototype, {
    setup() {
        super.setup();
        if (!this.currencyOptions.some((opt) => opt.value === "UGX")) {
            this.currencyOptions = [
                { value: "UGX", label: "UGX" },
                ...this.currencyOptions,
            ];
        }
    },
});
