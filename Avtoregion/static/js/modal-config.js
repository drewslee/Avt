$(function ()
{

    $(document).on("click", '#state', function ()
    {
        $('#ModalUpdate').modal('show');
    });

    $(document).on('click', '#delete_race', function ()
    {
        $('#id_modal_message').html('<p>Вы уверены?</p>');
        $('#delete_race_ok')[0].disabled = false;
        $('#ModalMessage').modal({backdrop: true})
    });

    $(document).on('hide.bs.modal', '#ModalMessage', function ()
    {
        location.reload();
    });

    $(document).on("click", '#update_state', function (event)
    {
        $('#update_state_ok')[0].disabled = false;
        $('#ModalAccountUpdate').modal('show');
    });

    $(document).on('hide.bs.modal', '#ModalAccountUpdate', function ()
    {
        if (typeof(Storage) !== "undefined") {
          var $daterange = sessionStorage.getItem('daterange');
          var $type =  sessionStorage.getItem('type');
          var $service = sessionStorage.getItem('service');
          var $supplier =  sessionStorage.getItem('supplier');
          var $mediator = sessionStorage.getItem('mediator');
          var $customer = sessionStorage.getItem('customer');
          var $load_place =  sessionStorage.getItem('load_place');
          var $unload_place =  sessionStorage.getItem('unload_place');
          var $product =  sessionStorage.getItem('product');
          var $state =  sessionStorage.getItem('state');

          var data = {
                daterange: $daterange,
                type: $type,
                service: $service,
                supplier: $supplier,
                mediator: $mediator,
                customer: $customer,
                load_place: $load_place,
                unload_place: $unload_place,
                product: $product,
                state: $state
            };
            $.post({
                url: $('#account-form').attr('action'),
                traditional: true,
                data: JSON.stringify(data),
                success: function (resp)
                {
                    $('#tab_res').html(resp['data']);
                }


            });
        }
    });
});