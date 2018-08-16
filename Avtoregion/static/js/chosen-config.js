$(function ()
{

    $('#account_product').chosen({
        placeholder_text_multiple: 'Выберите фракцию',
        width: '100%'
    });
    $('#account_supplier').chosen({
        placeholder_text_single: 'Выберите организацию',
        width: '100%'

    });
    $('#account_type').chosen({
        placeholder_text_single: 'Выберите тип отчёта',
        width: '100%'

    });
    $('#account_mediator').chosen({
        placeholder_text_single: 'Выберите организацию',
        width: '100%'

    });
    $('#account_customer').chosen({
        placeholder_text_single: 'Выберите организацию',
        inherit_select_classes: false,
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
});
