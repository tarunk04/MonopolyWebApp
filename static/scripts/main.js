        var socket = io();

        function getSocketObject(){
            return socket;
        }

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
            modifiedHTML = 'Players in lobby: '
            for(i in data){ modifiedHTML+= '<div>'+data[i]+'</div>';}
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
            
            console.log(chosenOwnCard, ownCardColor, ownCardCollection);
        }

        socket.on("choose_own_card", function(data, callback){
            $("#wait").css("display", "block");
            var propertyCards = $(".selfPlayer .Card");
            for(var i=0;i<propertyCards.length;i++)
            {
                propertyCards[i].innerHTML+='<button value="'+propertyCards[i].attributes['name'].value+'" onclick="chooseOwnCard(event)">Choose</button>';
            }
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
        }

        socket.on("choose_own_set", function(data, callback){
            $("#wait").css("display", "block");
            var elements = $("#collection .selfPlayer .propertyCollection .propertySet");
            for(var i =0 ;i< elements.length;i++){
                elements[i].innerHTML+='<button value="'+elements[i].attributes['name'].value+'" onclick="chooseOwnColor(event)">Choose</button>'
            }
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
        }

        socket.on("choose_own_property", function(data, callback){
            $("#wait").css("display", "block");
            var propertyCards = $(".selfPlayer .propertyCard");
            for(var i=0;i<propertyCards.length;i++)
            {
                propertyCards[i].innerHTML+='<button value="'+propertyCards[i].attributes['name'].value+'" onclick="chooseOwnProperty(event)">Choose</button>';
            }
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


        var playIndex = -1;
        function playCard(event){
            element = event.target;
            parent = element.parentElement;
            playIndex = Number(element.value[0]);
            if (element.value[1]=='A'){
                parent.innerHTML=element.value.substr(1,)+'<button value="1" onclick="cashOrAction(event)">Cash</button><button onclick="cashOrAction(event)" value="0">Action</button>';
            }
            console.log(playIndex);
        }

        socket.on('take_input',function(data,callback){
            $("#wait").css("display", "block");
            // socket.send()
        
            var myVar = setInterval(myTimer, 1000);

            function myTimer() {
                console.log('Waiting for chance');
                if(playIndex !=-1)
                {
                    clearInterval(myVar);
                    choice = playIndex;
                    console.log('Breaking out of loop');
                    callback({'value':choice});
                    playIndex = -1;
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
        }

        socket.on("choose_others_set", function(data, callback){
            $("#wait").css("display", "block");
            var elements = $("#collection .otherPlayer .propertyCollection .propertySet");
            for(var i =0 ;i< elements.length;i++){
                elements[i].innerHTML+='<button value="'+elements[i].attributes['name'].value+'" onclick="chooseOthersColor(event)">Choose</button>'
            }
            var myVar = setInterval(myTimer, 1000);

            function myTimer() {
                console.log('Waiting for chance');
                if(chosenOthersColor !="")
                {
                    clearInterval(myVar);
                    choice = chosenOthersColor;
                    console.log('Breaking out of loop');
                    callback({'value':choice,'playerId':otherPlayerId});
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
        }

        socket.on("choose_others_property", function(data, callback){
            $("#wait").css("display", "block");
            var propertyCards = $(".otherPlayer .propertyCard");
            for(var i=0;i<propertyCards.length;i++)
            {
                propertyCards[i].innerHTML+='<button value="'+propertyCards[i].attributes['name'].value+'" onclick="chooseOthersProperty(event)">Choose</button>';
            }
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
        }

        socket.on("choose_player", function(data, callback){
            $("#wait").css("display", "block");
            var otherPlayers = $(".otherPlayer");
            for(var i=0;i<otherPlayers.length;i++)
            {
                otherPlayers[i].innerHTML+='<button value="'+otherPlayers[i].id+'" onclick="choosePlayer(event)">Choose</button>';
            }
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
        }

        socket.on('cash_action',function(data,callback){
            $("#wait").css("display", "block");
            // socket.send()
        
            var myVar = setInterval(myTimer, 1000);

            function myTimer() {
                console.log('Waiting for chance');
                if(cashOrActionValue !=-1)
                {
                    clearInterval(myVar);
                    choice = cashOrActionValue;
                    console.log('Breaking out of loop');
                    callback({'value':choice});
                    cashOrActionValue = -1;
                    $("#wait").css("display", "none");
                }
                else
                console.log('Value still same');
            }
        });
          
        socket.on('game_data', function(data){
            console.log('GAME SETUP: ',data);
            collectionHTML = '';

            for(player in data['players']){
                
                propertyCollectionHTML = '<ul>';
                for(set in data['players'][player]['property_collection']){
                    thisSet = data['players'][player]['property_collection'][set];
                    if(thisSet.length!= 0) 
                    {
                        propertyCollectionHTML+='<li name="'+set+'" class="propertySet">';
                        propertyCollectionHTML+='<div>'+set+'</div>';
                        propertyCollectionHTML+='<ol>';
                        for(card in thisSet){
                            propertyCollectionHTML+= '<li name="'+thisSet[card]+'" class="propertyCard Card">'+thisSet[card]+'</li>'
                        }
                        propertyCollectionHTML+='</ol>';
                        propertyCollectionHTML+='</li>';

                    }
                }
                propertyCollectionHTML+= '</ul>';
                bankCollectionHTML = '<ul>';
                for(card in data['players'][player]['bank_collection']){
                    cardId = data['players'][player]['bank_collection'][card];
                    bankCollectionHTML += '<li name="'+cardId+'" class="bankCard Card">'+cardId+'</li>';
                }
                bankCollectionHTML+= '</ul>';
                otherPlayer = true;
                if(player == userId){
                    otherPlayer = false;
                }

                playerClass = "player ";
                if(otherPlayer)playerClass += "otherPlayer";
                else playerClass += "selfPlayer";

                collectionHTML+='<div id="'+player+'" class="'+playerClass+'">\
                <h2>'+data['players'][player]['username']+'</h2>\
                <div class="propertyCollection">\
                    <h4>Property Collection</h4>\
                    '+ propertyCollectionHTML + '\
                </div>\
                <div class="bankCollection">\
                    <h4>Bank Collection</h4>\
                    ' +  bankCollectionHTML + '\
                </div>\
            </div>';
            }
            $("#collection").html(collectionHTML);

        });

        socket.on('player_data', function(data){
            console.log('PLAYER SETUP: ',data);
            userId = data['id'];
            var chance  = false;
            if(data['chance'])
            chance = true;
            handCardHTML = '<h2>'+data['name']+'</h2><h4>Hand Card</h4><ul>';
            for(card in data['handcards']){
                handCardHTML += '<li>'+data['handcards'][card];
                if(chance){
                    handCardHTML+='<button onclick="playCard(event)" value="'+card + data['handcards'][card]+'">Play</button>';
                }
                handCardHTML+='</li>';
            }
            handCardHTML+= '</ul>';
            $("#handCards").html(handCardHTML);
        });
