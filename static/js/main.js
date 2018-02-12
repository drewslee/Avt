$(function () {
    $('input[name="daterange"]').daterangepicker({
        "autoApply": true,
        "alwaysShowCalendars": true,
        ranges: {
            'Этот месяц': [moment().startOf('month'), moment().endOf('month')],
            'Прошлый месяц': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
        },
        locale: {
            "fromLabel": "C",
            "toLabel": "По",
            "monthNames": [
                "Январь",
                "Февраль",
                "Март",
                "Апрель",
                "Май",
                "Июнь",
                "Июль",
                "Август",
                "Сентябрь",
                "Октябрь",
                "Ноябрь",
                "Декабрь"
            ],
            customRangeLabel: 'Свой диапазон',
            format: 'YYYY-MM-DD',
            "firstDay": 1,
            "weekLabel": "Неделя",
            "daysOfWeek": [
                "Вс",
                "Пн",
                "Вт",
                "Ср",
                "Чт",
                "Пт",
                "Сб"
            ]

        }
    });
    $('input[name="daterange"]').on('apply.daterangepicker', function (ev, picker) {
        $('form[id="push_date"]').submit()
    })
});

$(document).on('click', '.delete-confirmation', function () {
    return confirm('Вы уверены, что хотите удалить?');
});

$(function () {
    $('input[name="arrival_time"]').daterangepicker({
        "singleDatePicker": true,
        "autoApply": true,
        "timePicker": true,
        "timePicker24Hour": true,
        locale: {
            "monthNames": [
                "Январь",
                "Февраль",
                "Март",
                "Апрель",
                "Май",
                "Июнь",
                "Июль",
                "Август",
                "Сентябрь",
                "Октябрь",
                "Ноябрь",
                "Декабрь"
            ],
            format: 'YYYY-MM-DD H:mm',
            "firstDay": 1,
            "weekLabel": "Неделя",
            "daysOfWeek": [
                "Вс",
                "Пн",
                "Вт",
                "Ср",
                "Чт",
                "Пт",
                "Сб"
            ]

        }
    });
});
$(function () {
    $('input[name="race_date"]').daterangepicker({
        "singleDatePicker": true,
        "autoApply": true,
        "timePicker": true,
        "timePicker24Hour": true,
        locale: {
            "monthNames": [
                "Январь",
                "Февраль",
                "Март",
                "Апрель",
                "Май",
                "Июнь",
                "Июль",
                "Август",
                "Сентябрь",
                "Октябрь",
                "Ноябрь",
                "Декабрь"
            ],
            format: 'YYYY-MM-DD H:mm',
            "firstDay": 1,
            "weekLabel": "Неделя",
            "daysOfWeek": [
                "Вс",
                "Пн",
                "Вт",
                "Ср",
                "Чт",
                "Пт",
                "Сб"
            ]

        }
    });
});
