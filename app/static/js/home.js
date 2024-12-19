document.addEventListener('DOMContentLoaded', function () {
    const regButton = document.getElementById("reg-btn");
    const openButton = document.getElementById("open-btn");
    const AUTH_ENDPOINT = '/auth/';

    async function sendUserInfo() {
        if (!tg) {
            throw new Error('Эта функция доступна только в Telegram WebApp.');
        }

        const userId = tg.initDataUnsafe.user.id;
        const initData = tg.initDataUnsafe;

        const dataToHash = Object.entries(initData)
            .filter(([key]) => key !== 'hash')
            .map(([key, value]) => `${key}=${encodeURIComponent(JSON.stringify(value))}`)
            .sort().join('\n');


        const hash = CryptoJS.HmacSHA256(dataToHash, "WebAppData");


        const authorizationHeader = `tma ${Object.entries(initData).map(([key, value]) => `${key}=${encodeURIComponent(JSON.stringify(value))}`).join('&')}&hash=${hash}`;

        const loadingIndicator = document.createElement('div');
        loadingIndicator.textContent = 'Отправка...';
        loadingIndicator.style.cssText = 'display: block; margin: 10px auto; text-align: center;';
        regButton.parentNode.insertBefore(loadingIndicator, regButton.nextSibling);

        try {
            const response = await fetch(AUTH_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': authorizationHeader,
                },
                body: JSON.stringify({user_id: userId}),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({message: 'Ошибка на сервере'}));
                throw new Error(errorData.message || `Ошибка при отправке запроса (${response.status})`);
            }

            const data = await response.json();
            loadingIndicator.remove();
            return data;
        } catch (error) {
            loadingIndicator.remove();
            throw error;
        }
    }

    function showSuccessMessage(message) {
        if (tg?.showPopup) {
            tg.showPopup({title: 'Успех', message, buttons: [{type: 'close'}]});
        } else {
            alert(message);
        }
    }


    function showErrorMessage(message) {
        if (tg?.showPopup) {
            tg.showPopup({title: 'Ошибка', message, buttons: [{type: 'close'}]});
        } else {
            alert(message);
        }
    }

    regButton.addEventListener('click', async function () {
        window.location.href = '/reg';
        // try {
        //     const result = await sendUserInfo();
        //     showSuccessMessage(result.message || 'Информация о пользователе отправлена');
        // } catch (error) {
        //     showErrorMessage(error.message);
        // }
    });

    openButton.addEventListener('click', async function () {
        window.location.href = '/hackathon';
        // try {
        //     const result = await sendUserInfo();
        //     showSuccessMessage(result.message || 'Информация о пользователе отправлена');
        // } catch (error) {
        //     showErrorMessage(error.message);
        // }
    });
});


