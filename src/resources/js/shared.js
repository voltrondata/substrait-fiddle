import axios from "axios";
import {SubstraitParser} from "./substrait-parser";
import {buildGraph, drawGraph} from "./substrait-to-d3";

function readText(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      resolve(reader.result);
    }
    reader.onerror = reject;
    reader.readAsText(file);
  })
}

function readFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      resolve(reader.result);
    };
    reader.onerror = reject;
    reader.readAsArrayBuffer(file);
  })
}

async function validate(plan, status_func) {
  try { 
    validateRsp = await axios.post("/api/validate/", plan);
    status_func("Plan validation successful!");
  } catch (error){
    status_func(error.response.data["detail"]);
  }
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

export {readFile, readText, validate, plot};
