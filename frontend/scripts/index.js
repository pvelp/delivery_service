const menuButtons = document.querySelectorAll('.menu__button')
const menu__list = document.querySelector('.menu__list')
const template = document.getElementById('menu__card-template');
const menuOrder = document.querySelector('.menu__order')
let menuAvaliableItems;
let menuItems=[]
fetch('http://localhost:8000/products/') //запрос на получение всех блюд из бд
  .then(response => {
    if (!response.ok) {
      throw new Error('Ошибка HTTP, код ' + response.status);
    }
    return response.json();
  })
  .then(data => {
     menuItems = data.results;
    console.log(menuItems); //для отладки

  })
  .catch(error => {
    console.error('Ошибка при выполнении запроса:', error);
  });



/*let menuItems = [
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
*/
  let cartItems = localStorage.getItem('cartItems');
  let products = cartItems ? JSON.parse(cartItems) : [];
  
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
              removeAllEventListeners();
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
      const product = menuItems.find(item => item.name === name);
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
        if (item.type === menuType) {
            var clone = document.importNode(template.content, true);
            clone.querySelector('.product__name').textContent = item.name;
            clone.querySelector('.menu__card-image').src = item.photo;
            clone.querySelector('.product__weight').textContent = item.weight;
            clone.querySelector('.product__price').textContent = item.price;
            
            menu__list.appendChild(clone);
        }
    });

    // При добавлении товара в корзину, устанавливаем его количество в 1
    menuAvailableItems = document.querySelectorAll('.menu__item');
    menuAvailableItems = document.querySelectorAll('.menu__item');
    menuAvailableItems.forEach(function(item) {
        item.addEventListener('click', function() {
            const name = item.querySelector('.product__name').textContent;
            const photo = item.querySelector('.menu__card-image').src;
            const weight = item.querySelector('.product__weight').textContent;
            const price = item.querySelector('.product__price').textContent;
            const compose = item.querySelector('.product__compose').textContent;

            const existingProductIndex = products.findIndex(product => product.name === name);
            if (existingProductIndex !== -1) {
                // Если товар уже есть в корзине, увеличиваем его количество
                products[existingProductIndex].quantity++;
            } else {
                // Иначе добавляем новый товар в корзину с количеством 1
                products.push({
                    name: name,
                    photo: photo,
                    weight: weight,
                    price: price,
                    compose: compose,
                    quantity: 1
                });
            }

            updateLocalStorage(); // Обновляем данные в localStorage
            makeOrder(products); // Обновляем отображение корзины
        });
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
    updateLocalStorage();
    products.forEach(function(product) {
        let card = document.createElement('li'); // Карточка
        card.className = 'product__card';

        let orderImageContainer = document.createElement('div'); // Изображение в контейнере
        orderImageContainer.className = 'product__image-container';
        let image = document.createElement('img');
        image.className = 'product__image';
        image.src = product.photo;
        image.alt = product.name;
        
        let orderInfoContainer = document.createElement('div');
        orderInfoContainer.className = 'product__info-container'; // Контейнер для информации

        let name = document.createElement('h2'); // Название
        name.textContent = product.name;
        name.className = 'product__name';

        let weight = document.createElement('p'); // Вес
        weight.textContent = product.weight;
        weight.className = 'product__weight';

        let price = document.createElement('p'); //
        price.textContent = product.price;
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
                product.quantity = count; // Обновляем количество товара в объекте товара
                updateLocalStorage(); // Обновляем localStorage при изменении количества товаров
            } else {
                card.remove();
                totalOrderPrice -= parseInt(product.price);
                totalPrice.textContent = totalOrderPrice + ' ₽';
                totalOrderQuantity--;
                totalCount.textContent = totalOrderQuantity;
                const index = products.indexOf(product);
                if (index > -1) {
                    products.splice(index, 1); // Удаляем товар из массива, если его количество стало 0
                }
                updateLocalStorage(); // Обновляем localStorage при удалении товара из корзины
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
            product.quantity = count; // Обновляем количество товара в объекте товара
            updateLocalStorage(); // Обновляем localStorage при изменении количества товаров
        });

        let counter = document.createElement('p');
        counter.className = 'product__counter';
        counter.textContent = product.quantity || 1; // Устанавливаем количество товара из объекта товара, если оно есть

        plusMinusButtonContainer.appendChild(buttonMinus);
        plusMinusButtonContainer.appendChild(counter);
        plusMinusButtonContainer.appendChild(buttonPlus);
        orderImageContainer.appendChild(image);
        nameAndWeight.appendChild(name);
        nameAndWeight.appendChild(weight);
        orderInfoContainer.appendChild(nameAndWeight)
        orderInfoContainer.appendChild(plusMinusButtonContainer);
        orderInfoContainer.appendChild(price);
        card.appendChild(orderImageContainer);
        card.appendChild(orderInfoContainer);
        orderContainer.appendChild(card);
        totalOrderPrice += parseInt(product.price) * (product.quantity || 1); // Учитываем количество товара
        totalOrderQuantity += product.quantity || 1; // Учитываем количество товара
    });

    totalPrice.textContent = totalOrderPrice;
    totalCount.textContent = totalOrderQuantity;
}
function updateLocalStorage() {
  localStorage.setItem('cartItems', JSON.stringify(products));
}
  

makeOrder(products);
const orderButton = document.querySelector('.menu__order-button');

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
    makeOrder(products);
});

function moveFinalCostContainer() {
    var finalCostContainer = document.querySelector('.final__cost-container');
    var orderContainer = document.querySelector('.window__order-container-order');
    orderContainer.insertAdjacentElement('afterend', finalCostContainer);
}

function checkResolution() {
    var screenWidth = window.innerWidth;
    
    if (screenWidth <= 768) {
        moveFinalCostContainer();
    } else {
        document.querySelector('.window__order-pay-container').prepend(finalCostContainer);
    }
}

window.onload = checkResolution;
window.onresize = checkResolution;
document.querySelector(".enter__button").addEventListener("click", sendEnterRequest);
document.querySelector(".enter__registration-button").addEventListener("click", sendRegRequest);


function sendEnterRequest() { //пост на вход
    const email = document.querySelector(".email__enter").value;
    const password = document.querySelector(".password__enter").value;
  
    let data = {
      email: email,
      password: password
    };
  
    fetch('http://localhost:8000/jwt/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })
      .then(response => {
        if (response.ok) {
          window.window__enter.close();
          console.log("Вход выполнен успешно");
          document.querySelector('.galochka').style.borderLeftColor = "black";
          document.querySelector('.galochka').style.borderBottomColor = "black";
          document.querySelector('.enter__text').style.color = "transparent";
        } else {
          document.querySelector(".email__enter").style.borderColor = "red";
          document.querySelector(".password__enter").style.borderColor = "red";
          console.error("Не удалось выполнить вход");
        }
      })
      .catch(error => {
      console.error('Ошибка:', error);
    });
}

function sendRegRequest() { //пост на регистрацию
    let email = document.querySelector(".reg_email").value;
    let password = document.querySelector(".reg_password").value;
    let firstName = document.querySelector(".reg_name").value;
    let lastName = document.querySelector(".reg_surname").value;
    let phone = document.querySelector(".reg_phone").value;
    let dob = document.querySelector(".reg_data").value;
  
    let data = {
      email: email,
      password: password,
      first_name: firstName,
      last_name: lastName,
      phone: phone,
      date_of_birth: dob
    };
  
    fetch('http://localhost:8000/users/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    .then(response => {
      if (response.ok) {
        console.log("Регистрация выполнена успешно");

      } else {
        document.getElementById("emailField").style.borderColor = "red";
        document.getElementById("passwordField").style.borderColor = "red";
        console.error("Не удалось выполнить вход");
      }
    })
    .catch(error => {
      console.error('Ошибка:', error);
    });
  }

  function sendOrderData() {
    let totalPrice = document.querySelector('.final__cost');
    var selectedRadio = document.querySelector('input[name="payopt"]:checked');
    var label = document.querySelector('label[for="' + selectedRadio.id + '"]');
    var PayMethod = label.textContent.trim();
    var selectedRadioDel = document.querySelector('input[name="delopt"]:checked');
    var label = document.querySelector('label[for="' + selectedRadioDel.id + '"]');
    let DeliveryMethod = label.textContent.trim();
    let buyerPhone = document.querySelector(".ord_phone").textContent
    let buyerAddress = document.querySelector(".ord_addr").textContent
    let buyerName = document.querySelector(".ord_name").textContent
    let Promo = document.querySelector(".promo").textContent

    var orderData = {
      buyer_phone_number: buyerPhone,
      delivery_address: buyerAddress,
      buyer_name: buyerName,
      payment_method: PayMethod,
      delivery_method: DeliveryMethod,
      order_amount: totalPrice.textContent,
      promo: Promo
    };
  
    // Отправляем POST-запрос
    fetch('http://localhost:8000/order/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(orderData)
    })
    .then(response => {
      if (response.ok) {
        console.log('Данные успешно отправлены');
      } else {
        console.error('Ошибка отправки данных:', response.statusText);
      }
      
    })
      .catch(error => {
      console.error('Ошибка:', error);
    });
  }

document.querySelector('.enter__window-button-order').addEventListener('click', sendOrderData);
