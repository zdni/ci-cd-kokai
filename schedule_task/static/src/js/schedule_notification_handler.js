/** @odoo-module **/

import {decrement, increment} from "@mail/model/model_field_command";
import {registerPatch} from "@mail/model/model_core";

registerPatch({
    name: "MessagingNotificationHandler",
    recordMethods: {
        /**
         * @override
         */
        async _handleNotification(message) {
            if (message.type === "schedule.task/updated") {
                for (const scheduleMenuView of this.messaging.models.ScheduleerMenuView.all()) {
                    if (message.payload.schedule_created) {
                        scheduleMenuView.update({extraCount: increment()});
                    }
                    if (message.payload.schedule_deleted) {
                        scheduleMenuView.update({extraCount: decrement()});
                    }
                }
            }
            return this._super(message);
        },
    },
});
