const menuButtons = document.querySelectorAll('.menu__button')
const menu__list = document.querySelector('.menu__list')
const template = document.getElementById('menu__card-template');
const menuOrder = document.querySelector('.menu__order')
let menuAvaliableItems;
let menuItems=[]
const main_url = 'http://localhost'
async function fetchProducts(url) {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error('Ошибка HTTP, код ' + response.status);
    }
    const data = await response.json();
    const menuItems = data.results;
    if (data.next) {
      const nextResults = await fetchProducts(data.next);
      return menuItems.concat(nextResults);
    } else {
      return menuItems;
    }
  } catch (error) {
    console.error('Ошибка при выполнении запроса:', error);
    throw error;
  }
}

async function fetchAllProducts() {
  try {
    const initialUrl = main_url + '/products';
    const menuItems = await fetchProducts(initialUrl);
    return menuItems;
  } catch (error) {
    console.error('Ошибка при выполнении запроса:', error);
    return [];
  }
}


async function processMenuItems() {
  menuItems = await fetchAllProducts();
}

processMenuItems().then(() => {
  


  
/*let gavnoItems = [
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

const categoryToType = {
  1: "cоусы",
  2: "варенье",
  3: "выпечка",
  4: "тандыр",
  5: "молочка",
  6: "кофе",
  7: "бастурма и суджук",
  8: "компот",
  9: "салаты",
  10: "напитки",
  11: "овощные консервы",
  12: "десерты",
  13: "гарниры",
  14: "мангал",
  16: "вода",
  17: "Шаурма"
};
const acceptToken = localStorage.getItem('accept_token');
const refreshToken = localStorage.getItem('refresh_token');

if(acceptToken) {
  document.querySelector('.galochka').style.borderLeftColor = "black";
  document.querySelector('.galochka').style.borderBottomColor = "black";
  document.querySelector('.enter__text').style.color = "transparent";
}

function addTypeToProducts(products) {
  return products.map(product => {
    const type = categoryToType[product.category];
    return { ...product, type }; // Создаем новый объект с добавленным свойством type
  });
}

menuItems = addTypeToProducts(menuItems);


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
      const product = menuItems.find(item => item.title === name);
      orderOptionName.textContent = name;
      orderOptionPhoto.src = photo;
      orderOptionWeight.textContent = product.weight + ' гр';
      orderOptionPrice.textContent = price;
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
            clone.querySelector('.product__name').textContent = item.title;
            clone.querySelector('.menu__card-image').src = item.image;
            clone.querySelector('.product__weight').textContent = item.weight + ' гр';
            clone.querySelector('.product__price').textContent = item.price + ' ₽';
            
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
            const product = menuItems.find(item => item.title === name);

            makeOrder(products); // Обновляем отображение корзины
        });
    });
}
  
  
 /* const selfCheckbox = document.getElementById('self');
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
  *///Сокрытие инпутов при выборе "самовывоз"
  
  
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
                const removable = menuItems.find(item => item.title === product.name);
                const data = {
                  product_id: removable.id,
                };
                fetch(main_url + '/remove-from-cart/', {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                  },
                  body: JSON.stringify(data)
                })
                .then(response => {
                  
                  if (response.status === 404) {
                    throw new Error('Product not found');
                  } else if (response.status === 200) {
                    return response.json();
                  } else {
                    throw new Error('Failed to remove product from cart');
                  }
                })
                .then(responseData => {
                  return responseData;
                })
                .catch(error => {
                  console.error('Error:', error.message);
                  return null;
                });
                
            } else {
                card.remove();
                totalOrderPrice -= parseInt(product.price);
                totalPrice.textContent = totalOrderPrice + ' ₽';
                totalOrderQuantity--;
                totalCount.textContent = totalOrderQuantity;
                const index = products.indexOf(product);
                const removable = menuItems.find(item => item.title === product.name);
                const data = {
                  product_id: removable.id,
                };
                fetch(main_url + '/remove-from-cart/', {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                    
                  },
                  body: JSON.stringify(data)
                })
                .then(response => {
                  if (response.status === 404) {
                    throw new Error('Product not found');
                  } else if (response.status === 200) {
                    return response.json();
                  } else {
                    throw new Error('Failed to remove product from cart');
                  }
                })
                .then(responseData => {
                  return responseData;
                })
                .catch(error => {
                  console.error('Error:', error.message);
                  return null;
                });
                if (index > -1) {
                    products.splice(index, 1); // Удаляем товар из массива, если его количество стало 0
                    updateLocalStorage();
                } // Обновляем localStorage при удалении товара из корзины
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
                     const addable = menuItems.find(item => item.title === product.name);
                const data = {
                  product_id: addable.id,
                  quantity: 1
                };
                fetch(main_url + '/add-to-cart/', {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                   
                  },
                  body: JSON.stringify(data)
                })
                .then(response => {
                  if (!response.ok) {
                    if (response.status === 404) {
                      throw new Error('Product not found');
                    } else {
                      throw new Error('Failed to add product to cart');
                    }
                  }
                  return response.json();
                })
                .then(responseData => {
                  return responseData;
                })
                .catch(error => {
                  console.error('Error:', error.message);
                  return null;
                });    
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

    totalPrice.textContent = totalOrderPrice + '  ₽';
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
    const existingProductIndex = products.findIndex(product => product.name === name);
    const product = menuItems.find(item => item.title === name);
    const data = {
      product_id: product.id,
      quantity: 1
    };
    fetch(main_url + '/add-to-cart/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        
      },
      body: JSON.stringify(data)
    })
    .then(response => {
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Product not found');
        } else {
          throw new Error('Failed to add product to cart');
        }
      }
      return response.json();
    })
    .then(responseData => {
      return responseData;
    })
    .catch(error => {
      console.error('Error:', error.message);
      return null;
    });
    if (existingProductIndex !== -1) {
      // Если товар уже есть в корзине, уменьшаем его количество
      products[existingProductIndex].quantity--;
      if (products[existingProductIndex].quantity === 0) {
          // Если количество товара стало равным нулю, удаляем его из массива
          products.splice(existingProductIndex, 1);
          // Удаляем товар из localStorage
          updateLocalStorage();
      }
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
  
    fetch(main_url + '/jwt/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    .then(response => {
      if (response.ok) {
        return response.json(); // Преобразуем ответ в JSON
      } else {
        document.querySelector(".email__enter").style.borderColor = "red";
        document.querySelector(".password__enter").style.borderColor = "red";
        console.error("Не удалось выполнить вход");
        throw new Error('Не удалось выполнить вход');
      }
    })
    .then(data => {
      // Извлекаем токены из JSON-объекта
      const acceptToken = data.access;
      const refreshToken = data.refresh;
    
      // Сохраняем токены accept и refresh в localStorage
      localStorage.setItem('accept_token', acceptToken);
      localStorage.setItem('refresh_token', refreshToken);
    
      // Закрываем окно или что у вас там
      window.window__enter.close();
    
      // Ваша дальнейшая логика обработки успешного входа
      console.log("Вход выполнен успешно");
      document.querySelector('.galochka').style.borderLeftColor = "black";
      document.querySelector('.galochka').style.borderBottomColor = "black";
      document.querySelector('.enter__text').style.color = "transparent";
    })
    .catch(error => {
      console.error('Ошибка:', error);
    });
}

function sendRegRequest() { //пост на регистрацию
  let email = document.querySelector(".reg_email");
  let password = document.querySelector(".reg_password");
  let firstName = document.querySelector(".reg_name");
  let lastName = document.querySelector(".reg_surname");
  let phone = document.querySelector(".reg_phone");
  let dob = document.querySelector(".reg_data");

  let data = {
    email: email.value,
    password: password.value,
    first_name: firstName.value,
    last_name: lastName.value,
    phone: phone.value,
    date_of_birth: dob.value
  };

  fetch(main_url + '/users/', {
    method: 'POST',
    headers: {  
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  .then(response => {
    if (response.ok) {
      console.log("Регистрация выполнена успешно");
      window.window__registration.close();
    } else {
      response.json().then(errors => {
        console.error("Не удалось выполнить вход", errors);
        // Подсветить input поля в случае ошибок
        if (errors.email) email.classList.add('input_error');
        if (errors.password) password.classList.add('input_error');
        if (errors.first_name) firstName.classList.add('input_error');
        if (errors.last_name) lastName.classList.add('input_error');
        if (errors.phone) phone.classList.add('input_error');
        if (errors.date_of_birth) dob.classList.add('input_error');
      });
    }
  });
}

function clearFields() { // функция для очистки значений полей ввода
  let inputs = document.querySelectorAll('.input_field');
  inputs.forEach(input => {
      input.value = ''; // Очистить значение поля ввода
  });
}

function clearErrors() { // функция для очистки подсветки ошибок при закрытии окна
  let inputs = document.querySelectorAll('.input_field');
  inputs.forEach(input => {
      input.classList.remove('input_error');
  });
}

// Добавляем обработчик события beforeunload для очистки полей перед закрытием окна
window.addEventListener('beforeunload', () => {
  clearFields(); // очистить значения полей ввода перед закрытием окна
});

// Добавляем обработчик события закрытия окна
window.window__registration.addEventListener('close', clearErrors);

  function sendOrderData() {
    let totalPrice = document.querySelector('.final__cost');
    var selectedRadio = document.querySelector('input[name="payopt"]:checked');
    var label = document.querySelector('label[for="' + selectedRadio.id + '"]');
    var PayMethod = label.textContent.trim();
    if (PayMethod  === 'Картой  (Visa, Mastercard, МИР)') {
      PayMethod = 'online'
    }
    else {
      PayMethod = 'to_courier'
    }
    var selectedRadioDel = document.querySelector('input[name="delopt"]:checked');
    var label = document.querySelector('label[for="' + selectedRadioDel.id + '"]');
    let DeliveryMethod = label.textContent.trim();
    if (DeliveryMethod  === 'Курьер') {
      DeliveryMethod  = 'courier'
    }
    else {
      DeliveryMethod  = 'pickup'
    }
    let buyerPhone = document.querySelector(".ord_phone").value;
    let buyerAddress = document.querySelector(".ord_addr").value;
    let buyerName = document.querySelector(".ord_name").value;
    let Promo = document.querySelector(".promo").value;
    let orderPrice = parseFloat(totalPrice.textContent.slice(0, -2));
    var orderData = {
      buyer_phone_number: buyerPhone,
      delivery_address: buyerAddress,
      buyer_name: buyerName,
      payment_method: PayMethod,
      delivery_method: DeliveryMethod,
      order_amount: orderPrice,
      promo: Promo
    };
  

    fetch(main_url + '/order/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
   
      },
      body: JSON.stringify(orderData)
    })
    .then(response => {
      if (response.ok) {
        console.log('Данные успешно отправлены');
        window.window__order.close
      } else {
        console.error('Ошибка отправки данных:', response.statusText);
      }
      
    })
      .catch(error => {
      console.error('Ошибка:', error);
    });
  }

  document.querySelector('.promo__accept').addEventListener('click', function() {
    const promoCode = document.querySelector('.promo').value;

    fetch(main_url + '/apply-promo-code/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization':  'Bearer ' + acceptToken
        },
        body: JSON.stringify({ promo_code: promoCode })
    })
    .then(response => {
        if (!response.ok) {
            if (response.status === 403) {
                console.error('Forbidden:', response.statusText);
            } else if (response.status === 404) {
                console.error('Not Found:', response.statusText);
            } else {
                console.error('Server Error:', response.statusText);
            }
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Success:', data);
        console.log(data.total_amount)
        totalPrice.textContent = data.total_amount_with_discount + '  ₽'
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
function getCart(){

  fetch(main_url + '/cart',  {
    method: 'GET',
    headers: {
        'Content-Type': 'application/json',
    },
  })
      .then(response => {
          if (!response.ok) {
              throw new Error('Network response was not ok');
          }
          return response.json();
      })
      .then(data => {
          console.log(data);
          if(data.total_amount_with_discount) {
            totalPrice.textContent = data.total_amount_with_discount + '  ₽'
          }
          else {
            totalPrice.textContent = data.total_amount + '  ₽'
          }
      })
      .catch(error => {
          console.error('Error:', error);
      });
};

document.querySelector('.nav__basket').addEventListener('click', function() {
  getCart();
})
document.querySelector('.enter__window-button-order').addEventListener('click', sendOrderData);
function handleScreenWidthChange() {
  const screenWidth = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;

  // Получаем элементы, которые мы хотим изменить порядок
  const photoContainer = document.querySelector('.menu__order-photo-container');
  const orderName = document.querySelector('.menu__order-name');
  const orderWeight = document.querySelector('.menu__order-weight');

  // Если ширина экрана меньше или равна 768px
  if (screenWidth <= 1500) {
    // Вставляем блок с фото между заголовком и весом заказа
    const orderInfo = orderName.parentElement;
    orderInfo.insertBefore(photoContainer, orderWeight);
  } else {
    // Если ширина экрана больше 768px, возвращаем блок с фото в его исходное положение
    const orderInfo = document.querySelector('.menu__order-info');
    orderInfo.insertBefore(photoContainer, orderInfo.firstChild);
  }
}

// Вызываем функцию при загрузке страницы и при изменении размеров окна
window.addEventListener('load', handleScreenWidthChange);
window.addEventListener('resize', handleScreenWidthChange);
// Вызываем функцию при загрузке страницы и при изменении размеров окна
window.addEventListener('load', handleScreenWidthChange);
window.addEventListener('resize', handleScreenWidthChange);
});

