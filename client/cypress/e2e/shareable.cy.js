/// <reference types="cypress" />

describe("Substrait Fiddle Shareable Link test", () => {
  
    it("shareable link", { browser: 'electron' }, () => {
      cy.visit("/")

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
          return window.navigator.clipboard.readText();
        }).then((link) => {
          cy.visit(link);
          cy.wait(5000).then(()=>{
            cy.get("#editor").should("not.be.empty")
            cy.contains(".multiselect__tag", "1002").should("exist");
            cy.contains(".multiselect__tag", "2001").should("exist");
          });
      });
    });
  });
  