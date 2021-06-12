function expand() {
            let acc = document.getElementsByClassName("signature_button");
            let i;

            for (i = 0; i < acc.length; i++) {
                acc[i].addEventListener("click", function () {
                    /* Toggle between adding and removing the "active" class,
                    to highlight the button that controls the panel */
                    this.classList.toggle("active");

                    /* Toggle between hiding and showing the active panel */
                    let panel = this.nextElementSibling;
                    if (panel.style.display === "block") {
                        panel.style.display = "none";
                    } else {
                        panel.style.display = "block";
                    }
                });
            }
        }


        expand();

formElem.onsubmit = async (e) => {
    e.preventDefault();

    let select = document.querySelector('.uploaddoc');
    let input = select.querySelector('input[type="file"]');
    const token = select.querySelector('[name=csrfmiddlewaretoken]').value;

    let data = new FormData(formElem);
    data.append('usert', 'hubot');
    let response = await fetch("testUploadDoc", {
      method: 'POST',
      body: data,
      credentials: 'same-origin',
    });
    let result = await response.json();
    console.log(result);
    alert(result.message);
    console.log(result.info);
    let modalTable = document.getElementsByClassName('modalTable')[0];
    modalTable.style.pointerEvents= 'auto';
    modalTable.style.opacity = '1';
    fillInfoTable(result.info)

};

function fillInfoTable(infoArray){
    let infoTable = document.getElementById('infoTable');
    if (infoArray.length>0){
        document.getElementById('noDocsMessage').remove();
    }
    document.getElementById("docName").innerHTML=`Документ: ${infoArray[0].document_title}`;
    for (let i = 0; i < infoArray.length;i++){
        let newRow = infoTable.insertRow(infoTable.length);
        let cell = newRow.insertCell(0);
        cell.innerHTML = infoArray[i].user;
        cell = newRow.insertCell(1);
        cell.innerHTML = infoArray[i].signed_date;
        cell = newRow.insertCell(2);
        cell.innerHTML = infoArray[i].validated ? "Подтвержден" : "Не прошел проверку";
    }
}

formElem_sing_doc.onsubmit = async (e) => {
    e.preventDefault();

    let select = document.querySelector('.singdoc');
    const token = select.querySelector('[name=csrfmiddlewaretoken]').value;

    let data = new FormData(formElem_sing_doc);
    let response = await fetch("testSingDoc", {
      method: 'POST',
      body: data,
      credentials: 'same-origin',
    });
    let result = await response.json();
    console.log(result);
    //alert(result.message);
};


formElem_verify_doc.onsubmit = async (e) => {
    e.preventDefault();

    let select = document.querySelector('.verify');
    const token = select.querySelector('[name=csrfmiddlewaretoken]').value;

    let data = new FormData(formElem_verify_doc);
    let response = await fetch("testVerifyDoc", {
      method: 'POST',
      body: data,
      credentials: 'same-origin',
    });
    let result = await response.json();
    console.log(result);
    alert(result.message);
};

fillUserDocumentsTable();

async function  fillUserDocumentsTable(){
    let docTable = document.getElementById("docTable");
    let result = await fetch("testGetUsersDocs", {
        method: 'GET',
        credentials: "same-origin"
    }).then(async (response)=>  {
        return await response.json()
    });
    if(!result.success){
        return
    }

    let docs = result.docs;
    console.log(result.docs)
    for (let i = 0; i < docs.length;i++){
        let newRow = docTable.insertRow(docTable.length)
        let cell = newRow.insertCell(0)
        cell.innerHTML = docs[i].title;
        cell = newRow.insertCell(1)
        cell.innerHTML = docs[i].users.join(', ');
        cell = newRow.insertCell(2)
        cell.innerHTML = docs[i].date;
    }
}

document.querySelector('[href="#Close"]').addEventListener('click',function (event) {
            event.preventDefault()
            let modalTable = document.getElementsByClassName('modalTable')[0];
            modalTable.style.pointerEvents= 'none';
            modalTable.style.opacity = '0';
        })