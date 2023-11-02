/// <reference types="cypress" />

const fs = require("fs");

describe("Substrait Fiddle Upload Test", () => {
  beforeEach(() => {
    cy.visit("/");
  });

  it("upload binary file", () => {
    cy.get("button")
      .contains("Upload")
      .click()
      .url()
      .should("include", "/upload");

    cy.get("#status").should("have.text", "// Status\n");

    cy.get("svg").should("be.empty");

    cy.get("#file-upload").selectFile("../resources/plan.bin");

    cy.get("#status").should("contain", "Plan generation successful!");

    cy.get("svg").should("not.be.empty");

    cy.get("button").contains("Save as SVG").click();

    cy.readFile("cypress/downloads/substrait_plan.svg").then(() => {
      cy.task("deleteFile", "cypress/downloads/substrait_plan.svg");
    });

    cy.get("button").contains("Save as PNG").click();

    cy.readFile("cypress/downloads/substrait_plan.png").then(() => {
      cy.task("deleteFile", "cypress/downloads/substrait_plan.png");
    });
  });
});
