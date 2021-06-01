const search = document.querySelector('#company');
const search_but = document.querySelector('#searcher_but');

function searcherMinLength(){
    valuesearch = search.value;
    if (valuesearch.length > 2)
        search_but.disabled = false;
    else
        search_but.disabled = true;
}

$('#company').on('input', function() {
            searcherMinLength();
});

$('#company').on('change', function() {
            searcherMinLength();
});
