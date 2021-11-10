$(document).ready(function() {
    $('.sidenav').sidenav();
    $('.collapsible').collapsible();
    $('select').formSelect();
});

$("label").click(function() {
    $(this).parent().find("label").css({
        "background-color": "grey"
    });
    $(this).css({
        "background-color": "gold"
    });
    $(this).nextAll().css({
        "background-color": "gold"
    });
});