function updateTime(){

const now = new Date();

document.getElementById("date").innerText =
now.toLocaleDateString();

document.getElementById("time").innerText =
now.toLocaleTimeString();

}

setInterval(updateTime,1000);

updateTime();