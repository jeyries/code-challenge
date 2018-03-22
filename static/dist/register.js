
(function () {

    function error(txt) {
        app.message_danger = txt;
        app.message_success = null;
        console.log("error", txt);
    }

    function success(txt) {
        app.message_danger = null;
        app.message_success = txt;
        console.log("success", txt);
    }


    var app = new Vue({
        el: '#app',
        data: {
            message_danger: null,
            message_success: null,
            email: null,
            password: null,
            verify: null,
        },
        methods: {


            //////////////////////
            submit: function(event) {
                event.preventDefault();

                console.log("submit", this.email);

                this.message_danger = null;
                this.message_success = null;



                if (this.password == null || this.password.length < 8) {
                    error( "Password too short. At least 8 characters required." )
                    return
                }

                if (this.password != this.verify) {
                    error( "Passwords does not match." )
                    return
                }

                let that = this;
                
                fetch('/user/create', {
                    method: 'POST',
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        token: CODECHALLENGE.token,
                        email: this.email,
                        password: this.password,
                    })

                  }).then(function(response) {
                    if (!response.ok) {
                        console.log(response);
                        let message = response.status + " " + response.statusText;
                        console.log(message);
                        return response.json().then(function(object) {
                            console.log(object)
                            if (object.message) {
                                message = object.message;
                            }
                            throw Error(message);
                        }).catch(function(_error) {
                            throw Error(message);
                        })
                    }

                    return response.json()
              
                  }).then(function(json) {
                    console.log("done create user", json.user);
                    success( "created user "+ json.user.email+". you will be redirected to home page." );
                    setTimeout(() => {window.location.replace("/");}, 3000 )

                  }).catch(function(_error) {
                    error( _error.message );

                  })
          
               

            },

        }
    });
  

  
})();
  
  
  
  