import axios from "axios";

function validate(plan, status_func) {
    axios
      .post("/api/validate/", plan)
      .then((response) => console.log(response))
      .catch((error) => {
        console.log(error)
        status_func(error.response.data["detail"]);
      });
}

export {validate};
