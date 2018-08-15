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
        $('#ModalUpdate').modal('show');
    });

    $(document).on('hide.bs.modal', '#ModalUpdate', function ()
    {
        location.reload();
    });
});