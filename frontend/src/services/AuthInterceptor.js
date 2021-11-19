import axios from "axios";
import Vue from "vue";

import API from "@/services/API";

axios.defaults.withCredentials = true;
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "XCSRF-TOKEN";

let tokenRefreshing = false;

axios.interceptors.response.use(async response => {
    if (response.data.code === 0) {
        // вернуть без вмешательства
        return response;
    } else if (response.data.code === 100) {
        // обновить токен
        if (!tokenRefreshing) {
            // обновить jwt токен

            // заблокируем операции с обновлением токена, чтобы другие процессы не перебивали
            tokenRefreshing = true;

            let crash = false;

            try {
                // авторизовываемся и повторяем попытку начального запроса
                let tokenRequest = await axios.post(`${API.SERVER_URL}auth/token/refresh/`);

                if (tokenRequest.data.code === 0) {
                    // авторизация успешно сосотялось. Можно повторить запрос
                    let newResponse = await retryRequest(response.config);
                    if (newResponse) {
                        tokenRefreshing = false;
                        return newResponse;
                    } else {
                        crash = true;
                    }
                } else {
                    // авторищация не состоялась
                    if (tokenRequest.data.code === 100) {
                        window.location = "/#/login"
                        Vue.$toast.warning("Срок действия сессии истёк");
                    } else if (response.data.code === 101) {
                        window.location = "/#/login"
                        Vue.$toast.warning("Срок действия сессии истёк");

                    } else {
                        handleError(tokenRequest);
                    }
                }
            } catch (e) {
                // произошла ошибка
                handleHttpError(e);
            }
            tokenRefreshing = false;

            if (crash) throw new Error();
        } else {
            // подождать и повторить запрос
            await new Promise(r => setTimeout(r, 2000));
            let newResponse = await retryRequest(response.config);
            if (newResponse) {
                return newResponse;
            } else {
                throw new Error();
            }
        }
    } else if (response.data.code === 101) {
        window.location = "/#/login"
        Vue.$toast.warning("Срок действия сессии истёк");
    } else {
        throw new Error();
    }
}, error => {
    handleHttpError(error);
});

async function retryRequest(config) {
    let hasError = false;
    try {
        let newResponse = await axios.request(config);
        if (newResponse.data.code === 0) {
            return newResponse;
        } else {
            handleError(newResponse);
        }
    } catch (e) {
        hasError = true;
        handleHttpError(e);
    }
    if (hasError) throw new Error();
    return false;
}

function handleError(error) {
    let message = "Неизвестная ошибка";
    switch (error.data.code) {
        case 1:
            message = "В ходе выполнения запроса произошла неизвестная ошибка. Подробности в консоли";
            break;
        case 2:
            message = "Не предоставлен токен авторизации"
            break;
        case 100:
            message = "Не удалось выполнить авторизацию";
            break;
    }
    Vue.$toast.warning(message);
    console.log(message);
    console.log(error);
}

function handleHttpError(error) {
    Vue.$toast.error("В ходе выполнения запроса на стороне сервера произошла ошибка");
    console.log(error);
}

// function handleErrors(response) {
//   if (response.data.code === 2) {
//     Vue.$toast.error("Ошибка авторизации #2.");
//     window.location = "/#/login";
//   } else {
//     if (response.data.response) {
//       let messages = response.data.response;
//       messages instanceof Array ? messages.forEach(m => Vue.$toast.warning(m)) : Vue.$toast.warning(messages);
//     } else {
//       Vue.$toast.warning("Не удалось выполнить запрос. Подробнее в консоли.");
//     }
//     console.log(response.data);
//   }
// }