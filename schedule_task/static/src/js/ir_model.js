/** @odoo-module **/

import {attr, one} from "@mail/model/model_field";
import {registerModel} from "@mail/model/model_core";

registerModel({
    name: "ir.model.schedule",
    fields: {
        /**
         * Determines the name of the views that are available for this model.
         */
        availableWebViews: attr({
            compute() {
                // "kanban", 
                return ["list", "form", "activity"];
            },
        }),
        scheduleGroup: one("ScheduleGroup", {
            inverse: "irModel",
        }),
        iconUrl: attr(),
        id: attr({
            identifying: true,
        }),
        model: attr({
            required: true,
        }),
        name: attr(),
    },
});
