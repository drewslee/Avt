$(function ()
{

    $('#account_product').chosen({
        placeholder_text_multiple: 'Выберите фракцию',
        width: '100%'
    });
    $('#account_supplier').chosen({
        placeholder_text_single: 'Выберите поставщика',
        allow_single_deselect: true,
        width: '100%'

    });
    $('#account_type').chosen({
        placeholder_text_single: 'Выберите тип отчёта',
        width: '100%'

    });
    $('#account_mediator').chosen({
        placeholder_text_single: 'Выберите посредника',
        width: '100%'

    });
    $('#account_customer').chosen({
        placeholder_text_single: 'Выберите покупателя',
        inherit_select_classes: false,
        allow_single_deselect: true,
        width: '100%'

    });
    $('#account_service').chosen({
        disable_search: true,
        inherit_select_classes: false,
        width: '100%'

    });
    $('#account_state').chosen({
        placeholder_text_single: 'Выберите состояние рейса',
        disable_search: true,
        inherit_select_classes: false,
        allow_single_deselect: true,
        width: '100%'

    });
    $('#account_unload_place').chosen({
        placeholder_text_single: 'Выберите место разгрузки',
        inherit_select_classes: false,
        allow_single_deselect: true,
        width: '100%'

    });
    $('#account_load_place').chosen({
        placeholder_text_single: 'Выберите место погрузки',
        inherit_select_classes: false,
        allow_single_deselect: true,
        width: '100%'

    });

    $(".icon-select").chosenIcon({});

    $('#account_customer, #account_mediator, #account_unload_place').parent().hide();

    $('#account_type').on('change', function (event, params) {
        if (params.selected === 'supplier') {
            $('#account_customer, #account_mediator, #account_unload_place').parent().hide();
            $('#account_supplier, #account_load_place').parent().show();
        }
        if (params.selected === 'customer') {
            $('#account_supplier, #account_mediator, #account_load_place').parent().hide();
            $('#account_customer, #account_unload_place').parent().show();
        }
        if (params.selected === 'mediator') {
            $('#account_supplier, #account_customer, #account_unload_place , #account_load_place').parent().hide();
            $('#account_mediator').parent().show();
        }
    })
});
