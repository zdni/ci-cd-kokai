odoo.define('get_geolocation.form', function(require) {
  "use strict";
  var publicWidget = require('web.public.widget');

  publicWidget.registry.HrAttendances = publicWidget.Widget.extend({
    selector: '.web_get_location',
    events: {'click .get-location': '_get_location'},
    _get_location: function(ev) {
      console.log('function _get_location');
      var self = this;
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
          const {latitude,longitude} = position.coords;
          const coords = {latitude,longitude};
          console.log(coords);
          self._rpc({
            model: 'res.partner',
            method: 'get_partner_location',
            args: [[], coords],
          })
          .then(function(result) {
            window.location.reload();
          });
        });
      }
    },
  });
});