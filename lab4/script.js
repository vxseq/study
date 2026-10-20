const phrases=["fraza1","fraza2","fraza3","fraza4"];
const button=document.getElementById("phraseButton");
const result=document.getElementById("phraseResult");
function printphrase()
{
    result.textContent=phrases[Math.floor(Math.random()*phrases.length)];
}
button.addEventListener("click",printphrase);