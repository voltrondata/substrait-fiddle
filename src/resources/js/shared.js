import axios from "axios";
import {SubstraitParser} from "./substrait-parser";
import {buildGraph, drawGraph} from "./substrait-to-d3";

function validate(plan, status_func) {
    axios
      .post("/api/validate/", plan)
      .then(() => status_func("Plan validation successful!"))
      .catch((error) => {
        console.log(error)
        status_func(error.response.data["detail"]);
      });
}

function plot(plan, status_func){
  try {
    const subplan = new SubstraitParser(plan).planToNode(plan);
    const graph = buildGraph(subplan);
    drawGraph(graph["nodes"], graph["edges"]);
    status_func("Plan generation successful!");
  } catch (error) {
    console.log(error)
    status_func("Error generating plot: " + error)
  }
}

export {validate, plot};
