const companiesSelect = document.querySelector('#company');
const companiesVsSelect = document.querySelector('#vs');
const vsButton = document.querySelector('#vsbut');
const chart = document.querySelector('#myChart');


fetchData(`http://api.marketstack.com/v1/tickers?access_key=49baab260b59e1fdc245c6444ba0891d`, function (data) {
    showCompanies(data.data);
});

function showCompanies(companiesJson) {
    for (let i = 0; i < companiesJson.length; i++) {
        companiesSelect.innerHTML += `<option value="${companiesJson[i].symbol} - ${companiesJson[i].name}">${companiesJson[i].name}</option>`;
        companiesVsSelect.innerHTML += `<option value="${companiesJson[i].symbol} - ${companiesJson[i].name}">${companiesJson[i].name}</option>`;
    }
}

function preventDupes( select, index ) { //Función que evita que se repitan dos valores iguales
    var options = select.options,
        len = options.length;
    while( len--) {
        if (options[ len ].value != "selectv")
            options[ len ].disabled = false;
    }
    select.options[ index ].disabled = true;
    if( index === select.selectedIndex ) {
        alert('You\'ve already selected the item "' + select.options[index].text + '".\n\nPlease choose another.');
        this.selectedIndex = 0;
    }
    if (this.options[ index ].value != "selectv" && select.options[ select.selectedIndex ].value != "selectv")
        vsButton.disabled = false;
}

companiesSelect.onchange = function() {
    preventDupes.call(this, companiesVsSelect, this.selectedIndex );
};

companiesVsSelect.onchange = function() {
    preventDupes.call(this, companiesSelect, this.selectedIndex );
};

function onCompanySelected() {
    const selectedCompany = companiesSelect.value;
}

function fetchData(url, callback) {
    const request = new XMLHttpRequest();
    request.open('GET', url);
    request.responseType = 'json';
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            callback(request.response)
        }
    };
    request.send();
}