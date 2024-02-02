import axios from "axios";

const BASE_URL = "http://127.0.0.1:9090";

test("validate", async () => {
  let plan = await (
    await fetch("https://substrait.io/tutorial/final_plan.json")
  ).json();
  const expectedErrorStatus = new Error("Internal Server Error");
  const expectedErrorMessage = new Error(
    "configured recursion limit for URI resolution has been reached",
  );
  return axios
    .post(BASE_URL + "/api/route/validate/", {
      plan: plan,
      override_levels: [2001, 1],
    })
    .catch((error) => {
      expect(error.response.statusText).toContain(expectedErrorStatus.message);
      expect(error.response.data["detail"]).toContain(
        expectedErrorMessage.message,
      );
    });
});
