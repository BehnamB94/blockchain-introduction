function mine() {
  callGetAPI("/mine")
}

function get_chain() {
  callGetAPI("/get_chain")
}

function verify() {
  callGetAPI("/verify")
}

function add_transaction() {
  const sender = document.getElementById("sender").value
  const receiver = document.getElementById("receiver").value
  const amount = parseInt(document.getElementById("amount").value)
  callPostAPI("/add_transaction", { sender: sender, receiver: receiver, amount: amount })
}

function connect_node() {
  const node = document.getElementById("node").value
  callPostAPI("/connect_node", { nodes: [node] })
}

function replace_chain() {
  callGetAPI("/replace_chain")
}


function callGetAPI(address) {
  fetch(address)
    .then(response => response.json())
    .then(data => {
      document.getElementById("response").innerHTML = syntaxHighlight(data)
    })
}

function callPostAPI(address, body) {
  fetch(address, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  })
    .then(response => response.json())
    .then(data => {
      document.getElementById("response").innerHTML = syntaxHighlight(data)
    })
}

function syntaxHighlight(json) {
  if (typeof json != 'string') {
    json = JSON.stringify(json, undefined, 2);
  }
  json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
    var cls = 'number';
    if (/^"/.test(match)) {
      if (/:$/.test(match)) {
        cls = 'key';
      } else {
        cls = 'string';
      }
    } else if (/true|false/.test(match)) {
      cls = 'boolean';
    } else if (/null/.test(match)) {
      cls = 'null';
    }
    return '<span class="' + cls + '">' + match + '</span>';
  });
}