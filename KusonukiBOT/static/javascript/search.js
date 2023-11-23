$(function () {
    document.getElementById('searchInput').addEventListener('keyup', function() {
        let searchValue = this.value.toLowerCase();
        let tables = document.getElementsByClassName('table')
        // let tableRows = document.getElementById('table').getElementsByTagName('tr');

        for (let j = 0; j < tables.length; j++) {
            let tableRows = tables[j].getElementsByTagName('tr');
            for (let i = 1; i < tableRows.length; i++) {
                let rowText = tableRows[i].textContent.toLowerCase();
                if (rowText.indexOf(searchValue) > -1) {
                    tableRows[i].style.display = '';
                } else {
                    tableRows[i].style.display = 'none';
                }
            }
        }
      });
});