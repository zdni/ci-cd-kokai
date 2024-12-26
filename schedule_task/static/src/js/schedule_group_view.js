/** @odoo-module **/

import {one} from "@mail/model/model_field";
import {registerModel} from "@mail/model/model_core";

registerModel({
    name: "ScheduleGroupView",
    recordMethods: {
        /**
         * @param {MouseEvent} ev
         */
        onClickFilterButton(ev) {
            this.scheduleMenuViewOwner.update({isOpen: false});
            // Fetch the data from the button otherwise fetch the ones from the parent (.o_ActivityMenuView_activityGroup).
            const data = _.extend({}, $(ev.currentTarget).data(), $(ev.target).data());
            const context = {};
            let action_tree = 'schedule_task.schedule_task_action_user';
            if(data.domain == 'unread_notification') {
                action_tree = 'schedule_task.notification_action_user';
                context['search_default_unread'] = 1;
            } else if(data.domain == 'unread_task') {
                context['search_default_unread'] = 1;
            } else if(data.domain == 'process_task') {
                context['search_default_process'] = 1;
            } else if(data.domain == 'overdue_task') {
                context['search_default_overdue'] = 1;
            }

            this.env.services['action'].doAction(action_tree, {
                additionalContext: context,
                clearBreadcrumbs: true,
            });
        },
    },
    fields: {
        scheduleGroup: one("ScheduleGroup", {
            identifying: true,
            inverse: "scheduleGroupViews",
        }),
        scheduleMenuViewOwner: one("ScheduleMenuView", {
            identifying: true,
            inverse: "scheduleGroupViews",
        }),
    },
});
