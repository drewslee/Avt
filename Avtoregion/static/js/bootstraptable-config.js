$(function ()
{

    var $race_table = $('#race_table');
    var $car_table = $('#car_table');
    var $driver_table = $('#driver_table');
    var $customer_table = $('#customer_table');
    var $supplier_table = $('#supplier_table');
    var $product_table = $('#product_table');
    var $trailer_table = $('#trailer_table');
    var $mediator_table = $('#mediator_table');
    var $units_table = $('#units_table');

    $car_table.bootstrapTable({
        showColumns: true,
        locale: 'ru-RU',
        pagination: true,
        showPaginationSwitch: true,
        cookie: true,
        cookieIdTable: 'CarCookId',
        onColumnSearch: function ()
        {
            $car_table.bootstrapTable("resetSearch");
        }
    });

    $car_table.on('check.bs.table', function (event, row, $element)
    {
        $('#change_car')[0].setAttribute('href', row.id + '/update/');
        $('#delete_car input[name= "pk"]')[0].setAttribute('value', row.id);
    });

    $driver_table.bootstrapTable({
        showColumns: true,
        locale: 'ru-RU',
        pagination: true,
        showPaginationSwitch: true,
        cookie: true,
        cookieIdTable: 'DriverCookId',
        onColumnSearch: function ()
        {
            $driver_table.bootstrapTable("resetSearch");
        }
    });

    $driver_table.on('check.bs.table', function (event, row, $element)
    {
        $('#change_driver')[0].setAttribute('href', row.id + '/update/');
        $('#delete_driver input[name= "pk"]')[0].setAttribute('value', row.id);
    });

    $customer_table.bootstrapTable({
        showColumns: true,
        locale: 'ru-RU',
        pagination: true,
        showPaginationSwitch: true,
        cookie: true,
        cookieIdTable: 'CustomerCookId',
        onColumnSearch: function ()
        {
            $customer_table.bootstrapTable("resetSearch");
        }
    });

    $customer_table.on('check.bs.table', function (event, row, $element)
    {
        $('#change_customer')[0].setAttribute('href', row.id + '/update/');
        $('#delete_customer input[name= "pk"]')[0].setAttribute('value', row.id);
        $('#change_customer_shipment')[0].setAttribute('href', row.id + '/unload_place/');
    });

    $customer_table.on('dbl-click-row.bs.table', function (event, row, $element)
    {
        $('#change_customer')[0].setAttribute('href', row.id + '/update/');
    });

    $supplier_table.bootstrapTable({
        showColumns: true,
        locale: 'ru-RU',
        pagination: true,
        showPaginationSwitch: true,
        cookie: true,
        cookieIdTable: 'SupplierCookId',
        onColumnSearch: function ()
        {
            $supplier_table.bootstrapTable("resetSearch");
        }
    });

    $supplier_table.on('check.bs.table', function (event, row, $element)
    {
        $('#change_supplier')[0].setAttribute('href', row.id + '/update/');
        $('#delete_supplier input[name= "pk"]')[0].setAttribute('value', row.id);
        $('#change_supplier_load')[0].setAttribute('href', row.id + '/load_place/');
    });

    $supplier_table.on('dbl-click-row.bs.table', function (event, row, $element)
    {
        $('#change_supplier')[0].setAttribute('href', row.id + '/update/');
    });

    $product_table.bootstrapTable({
        showColumns: true,
        locale: 'ru-RU',
        pagination: true,
        showPaginationSwitch: true,
        cookie: true,
        cookieIdTable: 'ProductCookId',
        onColumnSearch: function ()
        {
            $product_table.bootstrapTable("resetSearch");
        }
    });

    $product_table.on('check.bs.table', function (event, row, $element)
    {
        $('#change_product')[0].setAttribute('href', row.id + '/update/');
        $('#delete_product input[name= "pk"]')[0].setAttribute('value', row.id);
    });

    $trailer_table.bootstrapTable({
        showColumns: true,
        locale: 'ru-RU',
        pagination: true,
        showPaginationSwitch: true,
        cookie: true,
        cookieIdTable: 'TrailerCookId',
        onColumnSearch: function ()
        {
            $trailer_table.bootstrapTable("resetSearch");
        }
    });

    $trailer_table.on('check.bs.table', function (event, row, $element)
    {
        $('#change_trailer')[0].setAttribute('href', row.id + '/update/');
        $('#delete_trailer input[name= "pk"]')[0].setAttribute('value', row.id);
    });

    $mediator_table.bootstrapTable({
        showColumns: true,
        locale: 'ru-RU',
        pagination: true,
        showPaginationSwitch: true,
        cookie: true,
        cookieIdTable: 'MediatorCookId',
        onColumnSearch: function ()
        {
            $mediator_table.bootstrapTable("resetSearch");
        }
    });

    $mediator_table.on('check.bs.table', function (event, row, $element)
    {
        $('#change_mediator')[0].setAttribute('href', row.id + '/update/');
        $('#delete_mediator input[name= "pk"]')[0].setAttribute('value', row.id);
    });

    $units_table.bootstrapTable({
        showColumns: true,
        locale: 'ru-RU',
        pagination: true,
        showPaginationSwitch: true,
        cookie: true,
        cookieIdTable: 'UnitCookId',
        onColumnSearch: function ()
        {
            $units_table.bootstrapTable("resetSearch");
        }
    });

    $units_table.on('check.bs.table', function (event, row, $element)
    {
        $('#change_unit')[0].setAttribute('href', row.id + '/update/');
        $('#delete_unit input[name= "pk"]')[0].setAttribute('value', row.id);
    });

    $race_table.bootstrapTable({
        showColumns: true,
        locale: 'ru-RU',
        pagination: true,
        showPaginationSwitch: true,
        cookie: true,
        cookieIdTable: 'RaceCookId',
        onDblClickRow: function (row, $element, field) {
            window.location.href = '/Race/update/' + row.id + '/' ;
        },
        rowStyle: function (row, index)
        {
            if (row.state.trim() === "Авария")
            {
                return {
                    css: {
                        "background-color": "Tomato",
                        "color": "white"
                    }
                }
            }

            if (row.state.trim() === "Создан")
            {
                return {
                    css: {
                        "background-color": "BlanchedAlmond",
                        "color": "black"
                    }
                }
            }
            if (row.state.trim() === "Загружен")
            {
                return {
                    css: {
                        "background-color": "lightblue",
                        "color": "black"
                    }
                }
            }
            if (row.state.trim() === "Выгружен")
            {
                return {
                    css: {
                        "background-color": "Teal",
                        "color": "white"
                    }
                }
            }
            if (row.state.trim() === "Закончен")
            {
                return {
                    css: {
                        "background-color": "MediumSeaGreen",
                        "color": "white"
                    }
                }
            }
            if (row.state.trim() === "Проведен")
            {
                return {
                    css: {
                        "background-color": "Orange",
                        "color": "white"
                    }
                }
            }
            return row
        },
        onColumnSearch: function ()
        {
            $('#race_table').bootstrapTable("resetSearch");
        },
        formatLoadingMessage: function ()
        {
            return '<span class="glyphicon glyphicon glyphicon-repeat glyphicon-animate"></span>'
        }
    });
});