chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "FILL_FORM") {
    console.log("Comando recibido desde el popup. Listo para extraer campos.");
    alert("¡Conectado al Copiloto!");
  }
});
