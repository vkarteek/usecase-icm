// tools/add.js
export async function addNumbersHandler({ a, b }) {
    const sum = Number(a) + Number(b);
    return {
      content: [
        { type: "text", text: `${sum}` },
        { type: "data", data: { a: Number(a), b: Number(b), sum } },
      ],
    };
  }
  