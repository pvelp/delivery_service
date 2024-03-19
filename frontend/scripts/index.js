const menuButtons = document.querySelectorAll('.menu__button')
const menu__list = document.querySelector('.menu__list')
const template = document.getElementById('menu__card-template');
const menuOrder = document.querySelector('.menu__order')
let menuAvaliableItems;
let menuItems = [
    { name: "Шашлык", photo: './images/testImages/test1.jpg',  weight: "200", price: "350", type: "шашлык", compose: "курица, соль" },
    { name: "Шашлык",photo: './images/testImages/test1.jpg', weight: "200", price: "350", type: "шашлык", compose: "баранина, соль" },
    { name: "Шашлык", photo: './images/testImages/test1.jpg',weight: "200", price: "350", type: "шашлык", compose: "свинина, соль" },
    { name: "Шашлык", photo: './images/testImages/test1.jpg',  weight: "200", price: "350", type: "шашлык", compose: "курица, соль" },
    { name: "Шашлык",photo: './images/testImages/test1.jpg', weight: "200", price: "350", type: "шашлык", compose: "баранина, соль" },
    { name: "Шашлык", photo: './images/testImages/test1.jpg',weight: "200", price: "350", type: "шашлык", compose: "свинина, соль" },
    { name: "Рыба", photo: './images/testImages/test1.jpg', weight: "300", price: "280", type: "овощи и рыба на мангале", compose: "рыба, овощи" },
    { name: "Шаурма", photo: './images/testImages/test1.jpg', weight: "150", price: "101", type: "шаурма", compose: "лаваш, мясо, соус, капуста, помидоры" },
    { name: "Гренки", photo: './images/testImages/test1.jpg', weight: "150", price: "102", type: "закуски", compose: "хлеб, чеснок, соль" },
    { name: "Борщ", photo: './images/testImages/test1.jpg', weight: "150", price: "103", type: "супы", compose: "свекла, томаты, мясо, соль" },
    { name: "Цезарь", photo: './images/testImages/test1.jpg', weight: "150", price: "104", type: "салаты", compose: "салат, курица, соус, сухари" },
    { name: "Пирожок", photo: './images/testImages/test1.jpg', weight: "150", price: "105", type: "выпечка", compose: "тесто, мясо, соль" },
    { name: "Пиво", photo: './images/testImages/test1.jpg', weight: "150", price: "300", type: "напитки", compose: "хмель, солод, вода" },
    { name: "Кетчуп", photo: './images/testImages/test1.jpg', weight: "150", price: "500", type: "соусы", compose: "томаты, соль"},
    // Дополнительные объекты блюд могут быть добавлены
  ];


addOnlyMenuTypeExamples('шашлык');

function clickButtonByText(buttonText) {
    const buttons = document.querySelectorAll('.menu__button'); 
    buttons.forEach(button => {
        if (button.textContent === buttonText) {
            button.click(); 
        }
    });
}

function activeButton(buttons) {
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            document.querySelector('.active').classList.remove('active');
            button.classList.add('active');
            addOnlyMenuTypeExamples(button.textContent);

            // Удаляем предыдущие обработчики событий
            removeAllEventListeners();

            // Добавляем обработчики для новых элементов
            const overlayElements = document.querySelectorAll('.menu__card-overlay');
            overlayElements.forEach(element => {
                element.addEventListener('click', handleClick);
            });
        });
    });
}

function removeAllEventListeners() {
    const overlayElements = document.querySelectorAll('.menu__card-overlay');
    overlayElements.forEach(element => {
        const newElement = element.cloneNode(true);
        element.parentNode.replaceChild(newElement, element);
    });
}

function handleClick() {
    const menuItem = this.closest('.menu__item');
    const name = menuItem.querySelector('.product__name').textContent;
    const photo = menuItem.querySelector('.menu__card-image').src;
    const weight = menuItem.querySelector('.product__weight').textContent;
    const price = menuItem.querySelector('.product__price').textContent;
    const orderOption = document.getElementById('menu__order');
    const orderOptionName = orderOption.querySelector('.menu__order-name');
    const orderOptionPhoto = orderOption.querySelector('.menu__order-photo');
    const orderOptionCompose = orderOption.querySelector('.menu__order-compose-list');
    const orderOptionWeight = orderOption.querySelector('.menu__order-weight');
    const orderOptionPrice = orderOption.querySelector('.menu__order-price');
    product = menuItems.find(product => product.name === name);
    orderOptionName.textContent = name;
    orderOptionPhoto.src = photo;
    orderOptionCompose.textContent = product.compose;
    orderOptionWeight.textContent = weight + ' гр';
    orderOptionPrice.textContent = price + ' ₽';
}

// Добавляем обработчики событий для кнопок меню
activeButton(menuButtons);

activeButton(menuButtons);
clickButtonByText('шашлык');


function addOnlyMenuTypeExamples(menuType) {
while (menu__list.firstChild) {
       menu__list.removeChild(menu__list.firstChild);
}

menuItems.forEach(function(item) {
    if (item.type === menuType){

    var clone = document.importNode(template.content, true);

    clone.querySelector('.product__name').textContent = item.name;
    clone.querySelector('.menu__card-image').src = item.photo;
    clone.querySelector('.product__weight').textContent = item.weight;
    clone.querySelector('.product__price').textContent = item.price;
    
    menu__list.appendChild(clone);
    }
});
}



const selfCheckbox = document.getElementById('self');
const courierCheckbox = document.getElementById('courier');
const inputContainer = document.querySelector('.input_container');
function toggleInputContainer() {
    if (selfCheckbox.checked) {
        inputContainer.style.display = 'none';
    } else {
        inputContainer.style.display = 'flex';
    }
}
toggleInputContainer();
selfCheckbox.addEventListener('change', toggleInputContainer);
courierCheckbox.addEventListener('change', toggleInputContainer);
//Сокрытие инпутов при выборе "самовывоз"


let orderContainer = document.querySelector('.window__order-container-order');
let totalPrice = document.querySelector('.final__cost');
let totalCount = document.querySelector('.quantity'); 

function makeOrder(products) {
    orderContainer.innerHTML = '';
    let totalOrderPrice = 0;
    let totalOrderQuantity = 0;
    products.forEach(function(product) {

        let card = document.createElement('li'); // Карточка
        card.className = 'product__card';

        let orderImageContainer = document.createElement('div'); // Изображение в контейнере
        orderImageContainer.className = 'product__image-container';
        let image = document.createElement('img');
        image.className = 'product__image';
        image.src = product.photo;
        image.alt = product.name;

        let orderInfoContaier = document.createElement('div'); 
        orderInfoContaier.className = 'product__info-container'; // Контейнер для информации

        let name = document.createElement('h2'); // Название
        name.textContent = product.name;
        name.className = 'product__name';

        let weight = document.createElement('p'); // Вес
        weight.textContent = product.weight + ' гр';
        weight.className = 'product__weight';

        let price = document.createElement('p'); // Цена
        price.textContent = product.price + ' ₽';
        price.className = 'product__price';

        let nameAndWeight = document.createElement('div');
        nameAndWeight.className = 'product__name-and-weight';

        let plusMinusButtonContainer = document.createElement('div');
        plusMinusButtonContainer.className = 'product__buttons-container';

        let buttonMinus = document.createElement('button');
        buttonMinus.className = 'product__button-minus';
        buttonMinus.textContent = '-';
        buttonMinus.addEventListener('click', function() {
            let count = parseInt(counter.textContent);
            if (count > 1) {
                count--;
                counter.textContent = count;
                price.textContent = count * parseInt(product.price) + ' ₽';
                weight.textContent = count * parseInt(product.weight) + ' гр';
                totalOrderPrice -= parseInt(product.price);
                totalPrice.textContent = totalOrderPrice + ' ₽';
                totalOrderQuantity--;
                totalCount.textContent = totalOrderQuantity;
            } else {
                card.remove();
                totalOrderPrice -= parseInt(product.price);
                totalPrice.textContent = totalOrderPrice + ' ₽';
                totalOrderQuantity--;
                totalCount.textContent = totalOrderQuantity;
            }    
        });

        let buttonPlus = document.createElement('button');
        buttonPlus.className = 'product__button-plus';
        buttonPlus.textContent = '+';
        buttonPlus.addEventListener('click', function() {
            let count = parseInt(counter.textContent);
            count++;
            counter.textContent = count;
            price.textContent = count * parseInt(product.price) + ' ₽';
            weight.textContent = count * parseInt(product.weight) + ' гр';
            totalOrderPrice += parseInt(product.price);
            totalPrice.textContent = totalOrderPrice + ' ₽';
            totalOrderQuantity++;
            totalCount.textContent = totalOrderQuantity;
        });

        let counter = document.createElement('p');
        counter.className = 'product__counter';
        counter.textContent = '1';

        plusMinusButtonContainer.appendChild(buttonMinus);
        plusMinusButtonContainer.appendChild(counter);
        plusMinusButtonContainer.appendChild(buttonPlus);   

        // Добавляем элементы в карточку товара
        orderImageContainer.appendChild(image);
        nameAndWeight.appendChild(name);
        nameAndWeight.appendChild(weight);
        orderInfoContaier.appendChild(nameAndWeight)
        orderInfoContaier.appendChild(plusMinusButtonContainer);
        orderInfoContaier.appendChild(price);
        card.appendChild(orderImageContainer);
        card.appendChild(orderInfoContaier);

        // Добавляем карточку товара в контейнер
        orderContainer.appendChild(card);

        // Обновляем общую сумму заказа и количество товаров
        totalOrderPrice += parseInt(product.price);
        totalOrderQuantity++;
    }); 

    // Обновляем общую сумму заказа и количество товаров на странице
    totalPrice.textContent = totalOrderPrice;
    totalCount.textContent = totalOrderQuantity;
}


const orderButton = document.querySelector('.menu__order-button');
let products = [];

orderButton.addEventListener('click', () => {
    const name = document.querySelector('.menu__order-name').textContent;
    const photo = document.querySelector('.menu__order-photo').src;
    const weight = document.querySelector('.menu__order-weight').textContent;
    const price = document.querySelector('.menu__order-price').textContent;

    const selectedProduct = {
        name: name,
        photo: photo,
        weight: weight,
        price: price
    };

    const existingProductIndex = products.findIndex(product => product.name === selectedProduct.name);
    if (existingProductIndex !== -1) {
        products[existingProductIndex].quantity++;
    } else {
        selectedProduct.quantity = 1;
        products.push(selectedProduct);
    }

    // Передаем обновленный массив products в функцию makeOrder
    makeOrder(products);
});

function moveFinalCostContainer() {
    var finalCostContainer = document.querySelector('.final__cost-container');
    var orderContainer = document.querySelector('.window__order-container-order');
    orderContainer.insertAdjacentElement('afterend', finalCostContainer);
}

// Функция для проверки разрешения экрана и выполнения перемещения
function checkResolution() {
    // Проверяем текущее разрешение экрана
    var screenWidth = window.innerWidth;
    
    if (screenWidth <= 768) {
        // Если разрешение экрана меньше или равно 768px, перемещаем finalCostContainer после window__order-container-order
        moveFinalCostContainer();
    } else {
        // Если разрешение экрана больше 768px, перемещаем finalCostContainer обратно в начало window__order-container
        document.querySelector('.window__order-pay-container').prepend(finalCostContainer);
    }
}

// Вызываем функцию при загрузке страницы и при изменении размера окна
window.onload = checkResolution;
window.onresize = checkResolution;