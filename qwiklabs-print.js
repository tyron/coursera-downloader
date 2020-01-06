var styles = `
body > div.header-container,
#main-wrapper > ql-lab-control-panel,
#launcher {
    display: none
}

body, body.lab-show .l-lab-main-body
{
    padding: 0 !important;
}

@media print {
    body.lab-show {
        display: block !important
    }
}
`

var styleSheet = document.createElement("style")
styleSheet.type = "text/css"
styleSheet.innerText = styles
document.head.appendChild(styleSheet)