module.exports = {
  root: true,
  env: {
    node: true,
  },
  extends: ["plugin:vue/essential", "eslint:recommended", "@vue/prettier"],
  parserOptions: {
    ecmaVersion: 2020,
  },
  globals: {
    test: "readonly",
    expect: "readonly",
  },
  ignorePatterns: ["cypress/**/*.js"],
};
