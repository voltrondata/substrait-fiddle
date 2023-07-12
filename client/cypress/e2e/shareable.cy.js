/// <reference types="cypress" />

describe("Substrait Fiddle Shareable Link test", () => {
    beforeEach(() => {
      cy.visit("/");
    });
  
    it("shareable link", () => {
      cy.get("select").select("sql");
  
      cy.get("#status").should("have.text", "// Status\n");
  
      cy.get("#editor")
        .click()
        .focused()
        .type("{ctrl}a")
        .clear()
        .type("select * from lineitem;");
    
      cy.get(".multiselect__tags").click();
      cy.contains(".multiselect__option", "2001")
        .click()
  
      cy.get("button").contains("Generate").click();
  
      cy.get("button").contains("Copy Link").click();
    
      cy.window().then((window) => {
        const link = window.navigator.clipboard.readText();
        return link;
      }).then((link) => {
        cy.visit(link);
        cy.get("#editor").should("not.be.empty")
        cy.contains(".multiselect__tag", "1002").should("exist");
        cy.contains(".multiselect__tag", "2001").should("exist");
    });
    });
  });
  