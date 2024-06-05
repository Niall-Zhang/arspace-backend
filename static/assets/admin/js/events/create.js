$(document).ready(function(){

    google.maps.event.addDomListener(window, 'load', initialize);
        function initialize() {
            let input = document.getElementById('id_location');
            let autocomplete = new google.maps.places.Autocomplete(input);
            autocomplete.addListener('place_changed', function () {
            let place = autocomplete.getPlace();
            $('#id_latitude').val(place.geometry['location'].lat());
            $('#id_longitude').val(place.geometry['location'].lng());
        });
    }
    
    let dtToday = new Date();
    
    let month = dtToday.getMonth() + 1;
    let day = dtToday.getDate();
    let year = dtToday.getFullYear();
    if(month < 10)
        month = '0' + month.toString();
    if(day < 10)
        day = '0' + day.toString();
    
    let maxDate = year + '-' + month + '-' + day;   
    $('#id_date').attr('min', maxDate);
});