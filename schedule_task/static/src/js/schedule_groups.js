/** @odoo-module **/

import {attr, many, one} from "@mail/model/model_field";
import {registerModel} from "@mail/model/model_core";

registerModel({
    name: "ScheduleGroup",
    modelMethods: {
        convertData(data) {
            return {
                domain: data.domain,
                irModel: {
                    iconUrl: data.icon,
                    id: data.id,
                    model: data.model,
                    name: data.name,
                },
                record_count: data.record_count,
            };
        },
    },
    // recordMethods: {
    //     /**
    //      * @private
    //      */
    //     _onChangePendingCount() {
    //         if (this.type === "tier_schedule" && this.pending_count === 0) {
    //             this.delete();
    //         }
    //     },
    // },
    fields: {
        scheduleGroupViews: many("ScheduleGroupView", {
            inverse: "scheduleGroup",
        }),
        domain: attr(),
        irModel: one("ir.model.schedule", {
            identifying: true,
            inverse: "scheduleGroup",
        }),
        record_count: attr({
            default: 0,
        }),
        type: attr(),
    },
    // onChanges: [
    //     {
    //         dependencies: ["pending_count", "type"],
    //         methodName: "_onChangePendingCount",
    //     },
    // ],
});
