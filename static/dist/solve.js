
(function () {


// 1. Define route components.
// These can be imported from other files
const Read = { template: '<div>Read</div>' }
const Code = { template: '<div>Code</div>' }
const Submit = { template: '<div>Submit</div>' }

// 2. Define some routes
// Each route should map to a component. The "component" can
// either be an actual component constructor created via
// `Vue.extend()`, or just a component options object.
// We'll talk about nested routes later.
const routes = [
  { path: '/read', component: Read },
  { path: '/code', component: Code },
  { path: '/submit', component: Submit },
]

// 3. Create the router instance and pass the `routes` option
// You can pass in additional options here, but let's
// keep it simple for now.
const router = new VueRouter({
  routes: routes,
  linkActiveClass: "active",
})

router.push('read')

  //////////////////////////////////

  const LANGUAGES = [
    { name: 'python', title: 'Python', comment:'Python 3' },
    { name: 'javascript', title: 'Javascript', comment:'Node.js 8' },
    { name: 'java', title: 'Java', comment:'Java 7' },
    { name: 'c', title: 'C', comment:'GCC 4' },
    { name: 'cpp', title: 'C++', comment:'GCC 4' },
    { name: 'swift', title: 'Swift', comment:'Swift 4.0' },
    { name: 'go', title: 'Go', comment:'Go 1.9' },
    { name: 'scala', title: 'Scala', comment:'Scala 2.11' },
  ];

  const TEMPLATE = `
for k in range(3): 
  print("hello world !")
`;

  var app = new Vue({
    router: router,
    el: '#app',
    data: {
      message: null,

      language_dropdown: {
        selected: LANGUAGES[0],
        text: LANGUAGES[0].title,
        languages: LANGUAGES,
      },
      
      answer: TEMPLATE,
      result: "",

      progress: {
        value: 0,
        max: 7,
        animated: false,
        variant: "primary",
      },

      task: null,
      timeoutID: null,
    },
    methods: {
      select: function (language) {
        console.log("select", language.name);
        this.language_dropdown.text = language.title;
        this.language_dropdown.selected = language;
      },

      //////////////////////
      submit: function() {
        let language = this.language_dropdown.selected
        if (!language){
          alert("Please select a language.");
          return;
        }
        console.log("submit", language.name);
        this.message = null;
        this.result = "Please wait ... ";
        this.progress.value = 1;
        this.progress.animated = false;

        let that = this;

        fetch('/submit', {
          method: 'POST',
          credentials: 'include',
          headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({
              challenge: CODECHALLENGE.challenge.identifier,
              language: this.language_dropdown.selected.name,
              answer: this.answer,
          })
        })
        .then(function(response) {

          if (response.status != 200){
            console.log("failure", response);
            that.message = response.statusText;
            //return;
          }
          
          return response.json()
    
        }).then(function(json) {
    
          console.log("done submit task", json.task)

          that.task = json.task;
          that.progress.animated = true;
          
          that.scheduleProgress();
    
        }).catch(function(ex) {
          console.log('parsing failed', ex)
        })

      },

      ///////////////////
      scheduleProgress: function() {
        let that = this;
        clearTimeout(this.timeoutID);
        this.timeoutID = setTimeout(() => {that.handleProgress()}, 1000 );
      },

      handleProgress: function() {
        //console.log("handleProgress")
    
        if (this.task == null) {
          console.log("no task")
          return
        }
    
        let that = this;
    
        fetch('/task/'+this.task.uuid )
        .then(function(response) {
          return response.json()
    
        }).then(function(json) {
    
          console.log("task", json.uuid, "state", json.state, "now", json.now)
    
          that.result = json.result;
          that.progress.value = json.now;
          that.progress.max = json.max;

          if (json.state != "done" && json.state != "failure") {
            that.scheduleProgress()
            return
          }
    
          console.log("result", json.result);
          that.progress.animated = false;

          if (json.state == "failure") {
            that.progress.variant = "danger"
          } else if (json.state == "done") {
            that.progress.variant = "success"
          } else {
            that.progress.variant = "primary"
          }
    
        }).catch(function(ex) {
          console.log('parsing failed', ex)
        })
    
        
      },



    }
  });


})();



