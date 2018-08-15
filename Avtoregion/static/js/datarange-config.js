$(function ()
{
    $('#id_race_date').daterangepicker({
        "singleDatePicker": true,
        "autoApply": true,
        "timePicker": true,
        "timePicker24Hour": true,
        "startDate": new Date(),
        "endDate" : new Date(),
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
    $('#id_arrival_time').daterangepicker({
        "singleDatePicker": true,
        "autoApply": true,
        "timePicker": true,
        "timePicker24Hour": true,
        "startDate": new Date(),
        "endDate" : new Date(),
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
    $('#id_arrival_time_update').daterangepicker({
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
            format: 'DD.MM.YYYY H:mm:ss',
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
    $('#id_race_date_update').daterangepicker({
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
            format: 'DD.MM.YYYY H:mm:ss',
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
    var $datarange = $('input[name="daterange"]');

    $datarange.daterangepicker({
        "autoApply": true,
        "parentEl": 'toolbar',
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
    $datarange.on('apply.daterangepicker', function (ev, picker)
    {
        $('form[id="push_date"]').submit()
    });

    $('#id_race_date').on('apply.daterangepicker', function (ev, picker)
    {
        $('#id_arrival_time').focus().select();
    });
    $('#id_arrival_time').on('apply.daterangepicker', function (ev, picker)
    {
        $('#id_car').focus().select();
    });

});