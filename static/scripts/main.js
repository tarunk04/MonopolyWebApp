//TODO: Once everything is complete 
//1. Refactor socket acceptors
//2. Instead of adding and removing buttons. Make them active and inactive.

        var socket = io();

        function getSocketObject(){
            return socket;
        }

        var audio = new Audio('/static/sounds/ding_trim.mp3');

        socket.on('connect', function() {
            socket.send(userName + ' has connected!');
        });

        socket.on('message', function(message){
            console.log(message);
        });

        function getRndInteger(min, max) {
            return Math.floor(Math.random() * (max - min + 1) ) + min;
        }

        var userName = 'player' + getRndInteger(100000,999999);
        var userId = '';
        var host = false;
        function submitUsername(){
            userName = $("#username").val();
            // console.log(userName);
            socket.send(userName + ' has connected!');
            $("#username").val('');
        }

        function switchToLobby(roomId){
            console.log('Room created', roomId);
            // window.location.replace('/rooms/'+roomId+'/');
            document.getElementById('home').style.display="none";
            document.getElementById('lobby').style.display="block";
            document.getElementById('lobbyRoomid').innerText=roomId;
            document.getElementById('board').style.display = "none";
            socket.emit('enter_lobby', roomId);
        }
        
        function createRoom(){
            roomId = getRndInteger(100000,999999);
            host = true;
            socket.emit('join',{'username':userName,'room':roomId, 'exists':0});
            switchToLobby(roomId);
        }

        function joinRoom(){
            roomId = $("#joinRoomId").val();
            roomId = Number(roomId);
            socket.emit('join',{'username':userName,'room':roomId, 'exists':1});
            switchToLobby(roomId);
        }


        socket.on('modify_lobby',function(data){
            modifiedHTML = '<h2>Players in lobby: </h2>'
            for(i in data){ modifiedHTML+= '<h4>'+data[i]+'</h4>';}
            document.getElementById("users").innerHTML = modifiedHTML;
            if (host)document.getElementById("lobby").getElementsByTagName("button")[0].style.display="block";
            console.log('Players in lobby: '+data);
        });

        function cueToStart(){
            socket.emit('cue_to_start', roomId);
        }

        socket.on('game_setup', function(data){
            document.getElementById('lobby').style.display="none";
            document.getElementById('board').style.display="block";
            document.getElementById('boardRoomid').innerText=roomId;
        });

            
        //+++++++++++++++++++++++++++++++++++++++++++6
        // Choose own Card

        var tempClassNo = 0;

        var chosenOwnCard = "";
        var ownCardColor = "";
        var ownCardCollection = "";
        function chooseOwnCard(event){
            element = event.target;
            if($(element).parents(".propertyCollection").length>0)
            {
                ownCardColor = $(element).parents(".propertySet")[0].attributes['name'].value;
                chosenOwnCard = element.value;
                ownCardCollection = "propertyCollection";
            }
            else{
                ownCardColor = "";
                chosenOwnCard = element.value;
                ownCardCollection = "bankCollection";
            }    
            $("."+element.className.split(" ")[0]).remove();            
            console.log(chosenOwnCard, ownCardColor, ownCardCollection);
        }

        socket.on("choose_own_card", function(data, callback){
            $("#wait").css("display", "block");
            var propertyCards = $(".selfPlayer .Card");
            for(var i=0;i<propertyCards.length;i++)
            {
                propertyCards[i].innerHTML+='<button value="'+propertyCards[i].attributes['name'].value+'" onclick="chooseOwnCard(event)" class = "justCreated'+tempClassNo+'">Choose</button>';
            }
            tempClassNo+=1;
            var myVar = setInterval(myTimer, 1000);

            function myTimer() {
                console.log('Waiting for chance');
                if(chosenOwnCard !="")
                {
                    clearInterval(myVar);
                    choice = chosenOwnCard;
                    console.log('Breaking out of loop');
                    callback({'value':choice,'color':ownCardColor, 'collection':ownCardCollection});
                    chosenOwnCard = "";
                    ownCardColor ="";
                    ownCardCollection = "";
                    $("#wait").css("display", "none");
                }
                else
                console.log('Value still same');
            }
        });

        //+++++++++++++++++++++++++++++++++++++++++++7
        // Choose own set

        var chosenOwnColor = "";
        function chooseOwnColor(event){
            element = event.target;
            chosenOwnColor = element.value;
            console.log(chosenOwnColor);
            $("."+element.className.split(" ")[0]).remove();
        }

        socket.on("choose_own_set", function(data, callback){
            $("#wait").css("display", "block");
            var elements = $("#collection .selfPlayer .propertyCollection .propertySet");
            for(var i =0 ;i< elements.length;i++){
                elements[i].innerHTML+='<button value="'+elements[i].attributes['name'].value+'" onclick="chooseOwnColor(event)" class = "justCreated'+tempClassNo+'">Choose</button>'
            }
            tempClassNo+=1;
            var myVar = setInterval(myTimer, 1000);

            function myTimer() {
                console.log('Waiting for chance');
                if(chosenOwnColor !="")
                {
                    clearInterval(myVar);
                    choice = chosenOwnColor;
                    console.log('Breaking out of loop');
                    callback({'color':choice});
                    chosenOwnColor = "";
                    $("#wait").css("display", "none");
                }
                else
                console.log('Value still same');
            }
        });

        //+++++++++++++++++++++++++++++++++++++++++++8
        // Choose own property

        var chosenOwnProperty = "";
        var ownPropertyColor = "";
        function chooseOwnProperty(event){
            element = event.target;
            ownPropertyColor = $(element).parents(".propertySet")[0].attributes['name'].value;
            chosenOwnProperty = element.value;
            console.log(chosenOwnProperty, ownPropertyColor);
            $("."+element.className.split(" ")[0]).remove();
        }

        socket.on("choose_own_property", function(data, callback){
            $("#wait").css("display", "block");
            var propertyCards = $(".selfPlayer .propertyCard");
            for(var i=0;i<propertyCards.length;i++)
            {
                propertyCards[i].innerHTML+='<button value="'+propertyCards[i].attributes['name'].value+'" onclick="chooseOwnProperty(event)" class = "justCreated'+tempClassNo+'">Choose</button>';
            }
            tempClassNo+=1;
            var myVar = setInterval(myTimer, 1000);

            function myTimer() {
                console.log('Waiting for chance');
                if(chosenOwnProperty !="")
                {
                    clearInterval(myVar);
                    choice = chosenOwnProperty;
                    console.log('Breaking out of loop');
                    callback({'value':choice,'color':ownPropertyColor});
                    chosenOwnProperty = "";
                    ownPropertyColor ="";
                    $("#wait").css("display", "none");
                }
                else
                console.log('Value still same');
            }
        });


        //+++++++++++++++++++++++++++++++++++++++++++1


        var playIndex = undefined;
        function playCard(event){
            element = event.target;
            parent = element.parentElement;
            playIndex = Number(element.value);
            // if (element.value[1]=='A'){
            //     parent.innerHTML=element.value.substr(1,)+'<button value="1" onclick="cashOrAction(event)" class = "justCreated'+tempClassNo+'">Cash</button><button onclick="cashOrAction(event)" value="0" class = "justCreated'+tempClassNo+'">Action</button>'; //TODO: Generalise the function for choice
            // }
            // tempClassNo+=1;
            $("."+element.className.split(" ")[0]).remove();
            console.log(playIndex);
        }

        socket.on('take_input',function(data,callback){
            $("#wait").css("display", "block");
            audio.play();
            // $(".handCard").append('<button onclick="playCard(event)" class = "justCreated'+tempClassNo+'">Play</button>');
            var elements = $(".handCard");
            for(var i =0;i<elements.length;i++)
            {   
                $(elements[i]).append('<button value="'+i+'" onclick="playCard(event)" class = "justCreated'+tempClassNo+'">Play</button>');
            }
            // socket.send()
            $("#handCards").append('<button value="-1" onclick="playCard(event)" class = "justCreated'+tempClassNo+'">PASS</button>');
            $("#handCards").append('<button value="-2" onclick="playCard(event)" class = "justCreated'+tempClassNo+'">ARRANGE</button>');
            tempClassNo+=1;
        
            var myVar = setInterval(myTimer, 1000);

            function myTimer() {
                console.log('Waiting for chance');
                if(playIndex!=undefined)
                {
                    clearInterval(myVar);
                    choice = playIndex;
                    console.log('Breaking out of loop');
                    callback({'value':choice});
                    playIndex = undefined;
                    $("#wait").css("display", "none");
                }
                else
                console.log('Value still same');
            }
        });

        //+++++++++++++++++++++++++++++++++++++++++++2

        var chosenOthersColor = "";
        // var otherPlayerId = "";
        function chooseOthersColor(event){
            element = event.target;
            otherPlayerId = $(element).parents(".player")[0].id;
            chosenOthersColor = element.value;
            console.log(chosenOthersColor);
            $("."+element.className.split(" ")[0]).remove();
        }

        socket.on("choose_others_set", function(data, callback){
            $("#wait").css("display", "block");
            var elements = $("#collection .otherPlayer .propertyCollection .propertySet");
            for(var i =0 ;i< elements.length;i++){
                elements[i].innerHTML+='<button value="'+elements[i].attributes['name'].value+'" onclick="chooseOthersColor(event)"  class = "justCreated'+tempClassNo+'">Choose</button>'
            }
            tempClassNo+=1;
            var myVar = setInterval(myTimer, 1000);

            function myTimer() {
                console.log('Waiting for chance');
                if(chosenOthersColor !="")
                {
                    clearInterval(myVar);
                    choice = chosenOthersColor;
                    console.log('Breaking out of loop');
                    callback({'color':choice,'playerId':otherPlayerId});
                    chosenOthersColor = "";
                    otherPlayerId = "";
                    $("#wait").css("display", "none");
                }
                else
                console.log('Value still same');
            }
        });

        //+++++++++++++++++++++++++++++++++++++++++++3

        var chosenOthersProperty = "";
        var otherPropertyColor = "";
        var otherPlayerId ="";
        function chooseOthersProperty(event){
            element = event.target;
            otherPropertyColor = $(element).parents(".propertySet")[0].attributes['name'].value;
            otherPlayerId = $(element).parents(".player")[0].id;
            chosenOthersProperty = element.value;
            console.log(chosenOthersProperty, otherPlayerId, otherPropertyColor);
            $("."+element.className.split(" ")[0]).remove();
        }

        socket.on("choose_others_property", function(data, callback){
            $("#wait").css("display", "block");
            var propertyCards = $(".otherPlayer .propertyCard");
            for(var i=0;i<propertyCards.length;i++)
            {
                propertyCards[i].innerHTML+='<button value="'+propertyCards[i].attributes['name'].value+'" onclick="chooseOthersProperty(event)"  class = "justCreated'+tempClassNo+'">Choose</button>';
            }
            tempClassNo+=1;
            var myVar = setInterval(myTimer, 1000);

            function myTimer() {
                console.log('Waiting for chance');
                if(chosenOthersProperty !="")
                {
                    clearInterval(myVar);
                    choice = chosenOthersProperty;
                    console.log('Breaking out of loop');
                    callback({'value':choice,'color':otherPropertyColor,'playerId':otherPlayerId});
                    chosenOthersProperty = "";
                    otherPlayerId ="";
                    otherPropertyColor ="";
                    $("#wait").css("display", "none");
                }
                else
                console.log('Value still same');
            }
        });


        //+++++++++++++++++++++++++++++++++++++++++++4


        var chosenPlayer = "";
        function choosePlayer(event){
            element = event.target;
            chosenPlayer = element.value;
            console.log(chosenPlayer);
            $("."+element.className.split(" ")[0]).remove();
        }

        socket.on("choose_player", function(data, callback){
            $("#wait").css("display", "block");
            var otherPlayers = $(".otherPlayerTab");
            for(var i=0;i<otherPlayers.length;i++)
            {
                otherPlayers[i].innerHTML+='<button value="'+otherPlayers[i].id.substr(0,2)+'" onclick="choosePlayer(event)" class = "justCreated'+tempClassNo+'">Choose</button>';
            }
            tempClassNo+=1;
            var myVar = setInterval(myTimer, 1000);

            function myTimer() {
                console.log('Waiting for chance');
                if(chosenPlayer !="")
                {
                    clearInterval(myVar);
                    choice = chosenPlayer;
                    console.log('Breaking out of loop');
                    callback({'playerId':choice});
                    chosenPlayer = "";
                    $("#wait").css("display", "none");
                }
                else
                console.log('Value still same');
            }
        });


        //+++++++++++++++++++++++++++++++++++++++++++5

        var cashOrActionValue = -1;
        function cashOrAction(event){
            element = event.target;
            cashOrActionValue = Number(element.value);
            console.log(cashOrActionValue);
            $("."+element.className.split(" ")[0]).remove();
        }

        var chosenValue = -1;
        function chooseValue(event){
            element = event.target;
            chosenValue = Number(element.value);
            console.log(chosenValue);
            $("."+element.className.split(" ")[0]).remove();            
        }

        socket.on('choose_value',function(data,callback){
            $("#wait").css("display", "block");
            // console.log('In choose value:', data);
            var choiceButtons = "";
            choiceButtons += '<span class = "justCreated'+tempClassNo+'">'+data['message']+'</span>';
            console.log("Choice Buttons HTML",choiceButtons);
            console.log(data);
            for(i in data){
                if(i!='message')
                choiceButtons+= '<button value="'+i+'" class = "justCreated'+tempClassNo+'" onclick=chooseValue(event)>'+data[i]+'</button>';
            }
            tempClassNo+=1;
            console.log(choiceButtons)
            $("#userInfo").html(choiceButtons)
            // socket.send()
        
            var myVar = setInterval(myTimer, 1000);

            function myTimer() {
                console.log('Waiting for chance');
                if(chosenValue !=-1)
                {
                    clearInterval(myVar);
                    choice = chosenValue;
                    console.log('Breaking out of loop');
                    callback({'value':choice});
                    chosenValue = -1;
                    $("#wait").css("display", "none");
                }
                else
                console.log('Value still same');
            }
        });
        var initialTabSetup = false;
        socket.on('game_data', function(data){
            console.log('GAME SETUP: ',data);
            collectionHTML = '';
            
            // console.log('This is the initial phase',initialTabSetup);
            if(initialTabSetup==false){
                var tabHTML = '';
                for(player in data['players']){
                    otherPlayer = true;
                    if(data['players'][player]['username'] == userName){
                        otherPlayer = false;
                    }

                    playerClass = "playerTab ";
                    if(otherPlayer)playerClass += "otherPlayerTab";
                    else playerClass += "selfPlayerTab";
                    tabHTML+='<li class="active"><a href="#'+player+'" id="'+player+'tab" class = "'+ playerClass+'"data-toggle="tab" data-target="#'+player+', #board" data-slide-to="'+player[1]+'">'+data['players'][player]['username']+'</a></li>';
                }
                // console.log("This is the inner html",tabHTML);
                $("#tabsInner").html(tabHTML);
                if(tabHTML!="")initialTabSetup=true;
            }

            for(player in data['players']){
                
                propertyCollectionHTML = '<ul class="propertySetList">';
                for(set in data['players'][player]['property_collection']){
                    thisSet = data['players'][player]['property_collection'][set];
                    if(thisSet.length!= 0) 
                    {
                        propertyCollectionHTML+='<li name="'+set+'" class="propertySet">';
                        // propertyCollectionHTML+='<div>'+set+'</div>';
                        propertyCollectionHTML+='<ul class="propertyCardList">';
                        var topDistance = 0;
                        var topDistanceAttribute = "";
                        for(card in thisSet){
                            var reverseClass = "";
                            if(thisSet[card].substr(1,2)=='WC' && thisSet[card].substr(3,2)!='XX' && thisSet[card].substr(3,2) != set)
                                    reverseClass = "reverseCard";
                            if(topDistance!=0)
                            topDistanceAttribute = 'position:absolute;top:'+topDistance+'%;'
                            else
                            topDistanceAttribute="";
                            propertyCollectionHTML+= '<li name="'+thisSet[card]+'" class="propertyCard Card" style="'+topDistanceAttribute+'"><img src ="/static/images/cards/'+thisSet[card]+'.svg" alt="Card" class="'+reverseClass+'" style="height:100%"></li>'
                            topDistance+=20;
                        }
                        propertyCollectionHTML+='</ul>';
                        propertyCollectionHTML+='</li>';
                    }
                }
                propertyCollectionHTML+= '</ul>';
                bankCollectionHTML = '<ul class="cashList">';
                for(card in data['players'][player]['bank_collection']){
                    cardId = data['players'][player]['bank_collection'][card];
                    bankCollectionHTML += '<li name="'+cardId+'" class="bankCard Card"><img src=/static/images/cards/'+cardId+'.svg alt="Card" height="100%"></li>';
                }
                bankCollectionHTML+= '</ul>';
                otherPlayer = true;
                if(player == userId){
                    otherPlayer = false;
                }

                playerClass = "player ";
                if(otherPlayer)playerClass += "item otherPlayer";
                else playerClass += "item selfPlayer active"; //By default collection of the player is shown

                collectionHTML+='<div id="'+player+'" class="'+playerClass+'">\
                <div class="row" style="height:100%">\
                <div class="col-md-8 propertyCollection" >\
                <span class="propertyValueSpan">Total Value: $'+data['players'][player]['totalValue']+'M</span>\
                    '+ propertyCollectionHTML + '\
                </div>\
                <div class="col-md-4 bankCollection">\
                <span class="bankValueSpan">Bank Value: $'+data['players'][player]['moneyValue']+'M</span>\
                    ' +  bankCollectionHTML + '\
                </div>\
                </div>\
            </div>';
            }
            $("#collection").html(collectionHTML);

        });

        socket.on('player_collection_data', function(data){
            console.log('PLAYER COLLECTION SETUP: ',data);
            collectionHTML = '';

            // for(collection in data){
                propertyCollectionHTML = '<ul class="propertySetList">';
                for(set in data['property_collection']){
                    thisSet = data['property_collection'][set];
                    if(thisSet.length!= 0) 
                    {
                        propertyCollectionHTML+='<li name="'+set+'" class="propertySet">';
                        // propertyCollectionHTML+='<div>'+set+'</div>';
                        propertyCollectionHTML+='<ul class="propertyCardList">';
                        var topDistance = 0;
                        var topDistanceAttribute = "";
                        for(card in thisSet){
                            var reverseClass = "";
                            if(thisSet[card].substr(1,2)=='WC' && thisSet[card].substr(3,2)!='XX'  && thisSet[card].substr(3,2) != set)
                                    reverseClass = "reverseCard";
                            if(topDistance!=0)
                            topDistanceAttribute = 'position:absolute;top:'+topDistance+'%;'
                            else
                            topDistanceAttribute="";
                            propertyCollectionHTML+= '<li name="'+thisSet[card]+'" class="propertyCard Card" style="'+topDistanceAttribute+'"><img src ="/static/images/cards/'+thisSet[card]+'.svg" alt="Card" class="'+reverseClass+'" style="height:100%"></li>'
                            topDistance+=20;
                        }
                        propertyCollectionHTML+='</ul>';
                        propertyCollectionHTML+='</li>';
                    }
                }
                propertyCollectionHTML+= '</ul>';
                bankCollectionHTML = '<ul class="cashList">';
                for(card in data['bank_collection']){
                    cardId = data['bank_collection'][card];
                    bankCollectionHTML += '<li name="'+cardId+'" class="bankCard Card"><img src=/static/images/cards/'+cardId+'.svg alt="Card" height="100%"></li>';
                }
                bankCollectionHTML+= '</ul>';
                otherPlayer = false;
                // if(player == userId){
                //     otherPlayer = false;
                // }

                playerClass = "player ";
                if(otherPlayer)playerClass += "item otherPlayer";
                else playerClass += "item selfPlayer active"; //By default collection of the player is shown

                collectionHTML+='<div id="'+userId+'" class="'+playerClass+'">\
                <div class="row" style="height:100%">\
                <div class="col-md-8 propertyCollection" >\
                <span class="propertyValueSpan">Total Value: $'+data['totalValue']+'M</span>\
                    '+ propertyCollectionHTML + '\
                </div>\
                <div class="col-md-4 bankCollection">\
                <span class="bankValueSpan">Bank Value: $'+data['moneyValue']+'M</span>\
                    ' +  bankCollectionHTML + '\
                </div>\
                </div>\
            </div>';
            $("#collection #"+userId).html(collectionHTML);
        });

        socket.on('player_data', function(data){
            console.log('PLAYER SETUP: ',data);
            userId = data['id'];
            var chance  = false;
            if(data['chance'])
            chance = true;
            handCardHTML = '';//'<h2>'+data['name']+'</h2><h4>Hand Card</h4>';
            // <div class="handCard"><img src="sampleGreen.svg" class="handCardImage" alt="Card"></div>
            for(card in data['handcards']){
                handCardHTML += '<div class="handCard"><img src="/static/images/cards/'+data['handcards'][card]+'.svg" class="handCardImage" alt="Card">';
                // if(chance){
                //     handCardHTML+='<button onclick="playCard(event)" value="'+card +'" class = "justCreated'+tempClassNo+'">Play</button>';
                // }
                handCardHTML+='</div>';
            }
            // if(chance)
            // handCardHTML+='<button onclick="playCard(event)" value="-1" class = "justCreated'+tempClassNo+'">PASS</button>';
            tempClassNo+=1;
            handCardHTML+= '</div>';
            $("#handCards").html(handCardHTML);
        });

        $("#collection").on('mousedown','.Card',function(event){
            element = event.target; 
            initPos = element.style.position;
            element.style.zIndex = 50; 
            if(initPos == "")
            element.style.position = 'relative';
            else
            element.style.position = 'absolute';
            setTimeout(()=>{
                element.style.zIndex = '';
                element.style.position = initPos;
            }, 3000);
        });

        // $("#collection").on('mouseup','.Card',function(event){
        //     element = event.target; 
        //     element.style.zIndex = ""; 
        // });

        socket.on('new_game', function(data){
            console.log('Entering lobby');
            setTimeout(()=>{switchToLobby(roomId);}, 3000);
        });

        const notificationContainer = document.getElementById('notification-container');

        const NOTIFICATION_TYPES = {
            INFO: 'info',
            SUCCESS: 'success',
            WARNING: 'warning',
            DANGER: 'danger'
        };

        function addNotification(type, text){
            const newNotification = document.createElement('div');
            newNotification.classList.add('notification', `notification-${type}`);
            
            const innerNotification = `${text}`;
            
            newNotification.innerHTML = innerNotification;
            
            notificationContainer.appendChild(newNotification);
            
            return newNotification;
        }

        function removeNotification(notification)
        {
            notification.classList.add('hide');
            setTimeout(()=>{
                notificationContainer.removeChild(notification);
            }, 500);
        }

        socket.on('notification', function(data,callback){
            console.log(data);
            // $("#userInfo").html('<p>'+data+'</p>');
            const info = addNotification(NOTIFICATION_TYPES.SUCCESS, data);

            setTimeout(() => {
                removeNotification(info);
            }, 20000);
        });
