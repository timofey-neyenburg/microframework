import uvicorn

from mf import Microframework, Request, Response


MF = Microframework()


@MF.get("/items")
async def handle_items(req: Request):
    return Response({"message": "ok"})


@MF.post("/items")
async def add_items(req: Request):
    return Response({"message": "added"}, status=201)


if __name__ == "__main__":
    uvicorn.run(
        MF,
        host="localhost",
        port=8080,
    )
