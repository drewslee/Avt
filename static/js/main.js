// This function gets cookie with a given name
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
/*
The functions below will create a header with csrftoken
*/
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}

/*    $('#race_table').bootstrapTable({
        showColumns: true,
        pagination: true,
        showPaginationSwitch: true,
        filterControl: true,
        columns: [
            {field: 'Машина' ,
                filterControl: 'select',
                filterStrictSearch: false,
                filterControlPlaceholder: ''}, {field:'Водитель', filterControl: 'select', filterStrictSearch: true}]

    });*/

$(function () {


    var csrftoken = getCookie('csrftoken');



    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });


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
    });

    $(document).on('click', '.delete-confirmation', function () {
        return confirm('Вы уверены, что хотите удалить?');
    });


    $('#race_table').bootstrapTable({
        showColumns: true,
        pagination: true,
        showPaginationSwitch: true,
        multipleSearch: true
    });
    $('.dropdown-toggle').dropdown();

    $(document).on("click", '#state', function () {
        $('#ModalUpdate').modal('show');
    });

    $(document).on("submit", '#update_state', function (event) {
        event.preventDefault();
        var rows = document.getElementsByClassName('selected'),
            list = [];
        for (var i = 0; i < rows.length; ++i) {
            list.push(rows[i].id);
        }
        var state = $('#status_select option:selected').text();
        $.ajax(
            {
                url: 'Race/update/ajax',
                method: 'POST',
                traditional: true,
                data: JSON.stringify({data: [{"id_list": list, "state": state}]}),
                dataType: 'json',
                success: function (resp) {
                    $('#ModalUpdate').modal('hide');
                },
                complete: function (resp) {
                    location.reload();
                }
            })
    });
    $(document).on("click", '#packing_list', function (event) {
        event.preventDefault();
        var rows = document.getElementsByClassName('selected'),
            list = [];
        for (var i = 0; i < rows.length; ++i) {
            list.push(rows[i].id);
        }
        $.ajax(
            {
                url: 'Race/packing/ajax',
                method: 'POST',
                traditional: true,
                data: JSON.stringify({"id_list": list}),
                dataType: 'json',
                success: function (data) {
                    $('#result').html(data['data']);
                    $('#ModalPackingList').modal('show');
                }
            })
    });

});

/*"responsive":    {
    breakpoints: [
        {name: 'bigdesktop', width: Infinity},
        {name: 'meddesktop', width: 1480},
        {name: 'smalldesktop', width: 1280},
        {name: 'medium', width: 1188},
        {name: 'tabletl', width: 1024},
        {name: 'btwtabllandp', width: 848},
        {name: 'tabletp', width: 768},
        {name: 'mobilel', width: 480},
        {name: 'mobilep', width: 320}
    ]
},*/
