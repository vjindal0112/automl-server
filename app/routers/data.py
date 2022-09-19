import json
from fastapi import APIRouter, UploadFile, Form, HTTPException
from typing import Dict, List
import pandas as pd
from sklearn.linear_model import LogisticRegression
from io import StringIO

router = APIRouter(
    prefix="/data",
    tags=["data"],
    responses={404: {"description": "Not found"},
               422: {"description:": "Unprocessable Entity"}},
)


def train_model_and_make_prediction(
    dataset: pd.DataFrame,
    output: str,
    inputs: List[str],
    hypothetical_input: Dict[str, float],
):
    assert dataset[output].dtype in (bool,)
    assert all(dataset[input].dtype in (float, int) for input in inputs)

    X = dataset[inputs]
    y = dataset[output]

    model = LogisticRegression()
    model.fit(X, y)

    prediction = model.predict_proba(
        pd.DataFrame({input: [hypothetical_input[input]] for input in inputs})
    )[0, model.classes_.tolist().index(True)]

    return prediction


@router.post("/upload")
async def upload_data(
    data: UploadFile,
):
    read_data = await data.read()
    read_data = str(read_data, "utf-8")
    dataset = pd.read_csv(StringIO(read_data))
    # upload to cloud storage bucket
    # save in database with unique id
    # process data
    # return columns and data types
    column_dict = {}
    if dataset.shape[0] < 1:
        raise HTTPException(status_code=422, detail="Dataset is empty")

    # only return the valid columns
    for col_name, val in dataset.iloc[:1].items():
        t = str(type(val.item()))
        if t == "<class 'bool'>":
            column_dict[col_name] = "bool"
        if t == "<class 'int'>":
            column_dict[col_name] = "int"
    json_data = dataset.to_json(orient="index")

    return {"types": column_dict, "data": json_data}


@router.post("/predict")
async def predict(
    dataset: UploadFile,
    output: str = Form(),
    inputs: str = Form(),
    hypothetical_input: str = Form(),
):
    # TODO: not type safe, would need to find workaround for future
    print(inputs)
    print(output)
    inputs = json.loads(inputs)
    hypothetical_input = json.loads(hypothetical_input)
    content = await dataset.read()
    data = str(content, 'utf-8')
    data = StringIO(data)
    dataset = pd.read_csv(data)
    print(dataset)
    prediction = train_model_and_make_prediction(
        dataset, output, inputs, hypothetical_input
    )
    return {"prediction": prediction}
