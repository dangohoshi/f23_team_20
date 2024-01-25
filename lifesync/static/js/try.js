let f = function () {
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function () {
        console.log(JSON.parse(this.responseText))
    }
    xhr.open("GET", "http://www.google.com", true)
    xhr.send()
}

f()