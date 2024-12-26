from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime, timedelta
from ..controllers import main as c

import json
import logging

_logger = logging.getLogger(__name__)

FINGERPRINTS = {
    "5": { "name" : "Muhammad Hasan", "department": "Production"},
    "6": { "name" : "Siti Arpati", "department": "HRGA"},
    "7": { "name" : "Diyet Prasetiya", "department": "Production"},
    "8": { "name" : "Edy Purnomo", "department": "HRGA"},
    "13": { "name" : "Deni Sumantri", "department": "Inventory & Logistic"},
    "14": { "name" : "Abdillah Rasyidi", "department": "Sales & Marketing"},
    "42": { "name" : "Gilang Yanuar Rahman", "department": "QHSE"},
    "47": { "name" : "M. Rizal Nurman Wahyu P.", "department": ""},
    "49": { "name" : "Kosasih", "department": "QHSE"},
    "81": { "name" : "81", "department": ""},
    "93": { "name" : "Widiya Febriany", "department": "HRGA"},
    "94": { "name" : "Meifi Khunsul Khotimah", "department": "HRGA"},
    "95": { "name" : "Anung Ari Setyawan", "department": "Production"},
    "100": { "name" : "100", "department": ""},
    "108": { "name" : "Agus Gunawan", "department": "Production"},
    "122": { "name" : "122", "department": ""},
    "123": { "name" : "123", "department": ""},
    "130": { "name" : "130", "department": ""},
    "221": { "name" : "221", "department": ""},
    "230": { "name" : "Tiara Rizqiah", "department": "QHSE"},
    "234": { "name" : "Heryane Endah Pratiwi", "department": "QHSE"},
    "235": { "name" : "Yudha Bakti Nugraha", "department": "QHSE"},
    "237": { "name" : "Hendry Wilzen", "department": "HRGA"},
    "245": { "name" : "Dwi Saputra", "department": "Production"},
    "251": { "name" : "251", "department": ""},
    "255": { "name" : "Yeni Anesia Murni", "department": "QHSE"},
    "261": { "name" : "Eka Sugiantini", "department": "Production"},
    "265": { "name" : "M. Rizky Noviyanti", "department": "Production"},
    "268": { "name" : "Galuh Indrawan", "department": "Production"},
    "274": { "name" : "Joko Frasetyo", "department": "Production"},
    "275": { "name" : "275", "department": ""},
    "276": { "name" : "Jamiludin", "department": "Production"},
    "282": { "name" : "Saiful Rizky", "department": "Production"},
    "283": { "name" : "Ian Bastiar", "department": "Production"},
    "287": { "name" : "Ahmad Syahru Robani", "department": "Production"},
    "288": { "name" : "288", "department": ""},
    "291": { "name" : "Alisia", "department": ""},
    "292": { "name" : "M. Huda Dimas Aditiya", "department": "Production"},
    "293": { "name" : "Mido", "department": ""},
    "294": { "name" : "Tri Wahyu Nugroho", "department": "Production"},
    "295": { "name" : "Feri", "department": ""},
    "296": { "name" : "Naufal", "department": ""},
    "297": { "name" : "Jifa", "department": ""},
    "298": { "name" : "Fahluzi", "department": ""},
    "299": { "name" : "M. Fathur Riza", "department": "Production"},
    "300": { "name" : "Sopian", "department": ""},
    "301": { "name" : "Yulia", "department": ""},
    "302": { "name" : "Novi", "department": ""},
    "303": { "name" : "Royyan", "department": ""},
    "304": { "name" : "Eko", "department": ""},
    "305": { "name" : "Anfal Juliansyah", "department": "QHSE"},
    "306": { "name" : "Dennis", "department": ""},
    "307": { "name" : "Sabbili Ramadhan", "department": "Inventory & Logistic"},
    "308": { "name" : "Dimas Anggara", "department": "Inventory & Logistic"},
    "309": { "name" : "Rakha", "department": ""},
    "310": { "name" : "Oscar", "department": ""},
    "311": { "name" : "Yeni Lestari Aruma I", "department": "Inventory & Logistic"},
    "312": { "name" : "Sandi", "department": ""},
    "313": { "name" : "Diah Larasati", "department": "FAT"},
    "314": { "name" : "Devita Wulandari", "department": "QHSE"},
    "315": { "name" : "Anggi Dita Sari Nasution", "department": "Purchasing"},
    "316": { "name" : "Syaiful Arief", "department": ""},
    "317": { "name" : "Erika", "department": ""},
    "318": { "name" : "Indah", "department": ""},
    "319": { "name" : "Achmad", "department": ""},
    "320": { "name" : "Aulia", "department": ""},
    "321": { "name" : "Maulana Cahya Putra", "department": "Inventory & Logistic"},
    "322": { "name" : "Elis", "department": ""},
    "333": { "name" : "Anastasia", "department": ""},
    "334": { "name" : "Abiyan Fitri Maulana", "department": "Inventory & Logistic"},
    "335": { "name" : "Ilmi", "department": ""},
    "336": { "name" : "Vanes", "department": ""},
    "337": { "name" : "M. Rizki", "department": ""},
    "338": { "name" : "Fatih", "department": ""},
    "339": { "name" : "Ahmad Raflyiansyah", "department": "Inventory & Logistic"},
    "340": { "name" : "Ersya", "department": ""},
    "341": { "name" : "Rangga Rafael", "department": "Production"},
    "342": { "name" : "Vivi Agustina", "department": "Engineering & Product Dev"},
    "343": { "name" : "Ariel", "department": ""},
    "344": { "name" : "Iik", "department": ""},
    "345": { "name" : "Agus Cahyono", "department": "Production"},
    "346": { "name" : "Andre Andika Tarigan", "department": "Engineering & Product Dev"},
    "347": { "name" : "Irsyad", "department": ""},
    "348": { "name" : "Rifky", "department": ""},
    "349": { "name" : "Soemanthoo Khoe", "department": "Production"},
    "350": { "name" : "Riyan", "department": ""},
    "351": { "name" : "Khanif Farichin", "department": "Production"},
    "352": { "name" : "Noviyan", "department": ""},
    "353": { "name" : "Julian", "department": ""},
    "354": { "name" : "Fajar", "department": ""},
    "355": { "name" : "Galang", "department": ""},
    "356": { "name" : "Haris", "department": ""},
    "357": { "name" : "Riski M", "department": ""},
    "358": { "name" : "Aslikan", "department": ""},
    "359": { "name" : "Angger", "department": ""},
    "360": { "name" : "Rohimat", "department": ""},
    "361": { "name" : "Yudi", "department": ""},
    "362": { "name" : "Arief Budi Saksono", "department": "Sales & Marketing"},
    "363": { "name" : "Holidatus Holida", "department": "Production"},
    "364": { "name" : "Tamara Rossa", "department": "Sales & Marketing"},
    "365": { "name" : "Tasya", "department": ""},
    "366": { "name" : "Tony", "department": ""},
    "367": { "name" : "Fiya", "department": ""},
    "368": { "name" : "Rawina Ferta Wijaya", "department": "Inventory & Logistic"},
    "369": { "name" : "Timu Sultan Agung", "department": "Purchasing"},
    "370": { "name" : "Ochta", "department": ""},
    "371": { "name" : "Miftah", "department": ""},
    "372": { "name" : "Yoga Darmawan", "department": "Production"},
    "373": { "name" : "M. Markus", "department": ""},
    "374": { "name" : "Bagas", "department": ""},
    "375": { "name" : "Ahmad Ashfa Mustofa", "department": "Production"},
    "376": { "name" : "Raflyansyah", "department": "Inventory & Logistic"},
    "377": { "name" : "Rozaq", "department": ""},
    "378": { "name" : "378", "department": ""},
    "379": { "name" : "Chairul Fajar Demokrasi", "department": "HRGA"},
    "380": { "name" : "Taufiq Hidayat", "department": "Production"},
    "381": { "name" : "Lucky William Piere Maharadja", "department": "Production"},
    "382": { "name" : "Muhammad Ridwan", "department": "Production"},
    "383": { "name" : "Ilham", "department": ""},
    "384": { "name" : "Hery", "department": ""},
    "385": { "name" : "Anggy", "department": ""},
    "386": { "name" : "Hafid Ridho Dhuhriansyah", "department": "Inventory & Logistic"},
    "387": { "name" : "Teddy", "department": ""},
    "388": { "name" : "Endah Irawati", "department": "Sales & Marketing"},
    "389": { "name" : "Arum", "department": ""},
    "390": { "name" : "Eka Putri cahyani", "department": "Inventory & Logistic"},
    "391": { "name" : "Lina Putri ", "department": "HRGA"},
    "392": { "name" : "Yuliandani", "department": "HRGA"},
    "393": { "name" : "Farrel Bayuputra Permana", "department": "HRGA"},
    "394": { "name" : "Indrik", "department": "Production"},
    "395": { "name" : "Adhiandra Vino S", "department": "Production"},
    "396": { "name" : "M. Miftahul Falah", "department": "Production"},
    "397": { "name" : "Fairuz Rasyid K", "department": "Production"},
    "398": { "name" : "Asep Deri Kristanto", "department": "Production"},
    "399": { "name" : "Fardan Ar Rizki", "department": "Production"},
    "400": { "name" : "Al Zidni Kasim", "department": "HRGA"},
    "401": { "name" : "M. Fairuz Ikhwani", "department": "HRGA"},
    "402": { "name" : "Annisa", "department": "QHSE"},
    "403": { "name" : "Indah Ranika", "department": "Sales & Marketing"}
}

class EmployeeAttendanceWizard(models.TransientModel):
    _name = 'employee.attendance.wizard'
    _description = 'Employee Attendance Wizard'

    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    get_by = fields.Selection([
        ('all', 'All'),
        ('department', 'Department'),
        ('employee', 'Employee'),
    ], string='Get By', required=True, default='all')
    department_ids = fields.Many2many('hr.department', string='Department')
    employee_ids = fields.Many2many('hr.employee', string='Employee')
    device_id = fields.Many2one('fingerprint.device', string='Device', required=True)

    def action_confirm(self):
        self.ensure_one()
        data = {}
        data['start_date'] = self.start_date
        data['end_date'] = self.end_date
        data['attendances'] = {}

        if not self.device_id:
            raise ValidationError("Choose Fingerprint Device to connect!")

        attendances = c.DeviceUsers.get_attendance(self.device_id)
        for attendance in attendances:
            user_id = attendance[0]
            if user_id in ["221", '389']:
                continue

            employee_name = user_id
            department = ""
            if FINGERPRINTS.get(user_id):
                employee_name = FINGERPRINTS[user_id]['name']
                department = FINGERPRINTS[user_id]['department']
            display_name = f"{department} - {employee_name}"


            attendance_date = attendance[1].date()
            punch = attendance[2]

            if attendance_date < self.start_date or attendance_date > self.end_date:
                continue

            if not display_name in data['attendances']:
                data['attendances'][display_name] = [employee_name, department, {}]

            if not attendance_date.strftime('%Y-%m-%d') in data['attendances'][display_name][2]:
                data['attendances'][display_name][2][attendance_date.strftime('%Y-%m-%d')] = []

            data['attendances'][display_name][2][attendance_date.strftime('%Y-%m-%d')].append([attendance[1], punch])
        sorted_attendances = dict(sorted(data["attendances"].items()))
        data["attendances"] = sorted_attendances
        
        if (not self.env.user.company_id.logo):
            raise UserError(_("You have to set a logo or a layout for your company."))
        elif (not self.env.user.company_id.external_report_layout_id):
            raise UserError(_("You have to set your reports's header and footer layout."))

        return self.env.ref('zk_attendance.action_report_employee_attendance_xlsx').report_action(self, data=data)