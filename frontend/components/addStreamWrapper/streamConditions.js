import styles from '../../styles/Editor.module.css'

import Button from 'react-bootstrap/Button'
import Form from 'react-bootstrap/Form'
import Modal from 'react-bootstrap/Modal'
import Table from 'react-bootstrap/Table'

import Select from 'react-select'
import { useState } from 'react'

import streamConditionOperators from '../../helpers/streamConditionOperators'

const StreamConditions = (props) => {

    const [conditions, setConditions] = useState([])

    const txtConditionColumnChangeHandler = (index, value)=> {
        let updatedConditions = props.conditions
        updatedConditions[index].column = value
        setConditions(updatedConditions)
        updateConditions(updatedConditions)
    }

    const selectOperatorChangeHandler = (index, operator)=> {
        let updatedConditions = props.conditions
        updatedConditions[index].operator = operator.value
        setConditions(updatedConditions)
        updateConditions(updatedConditions)
    }

    const txtConditionValueChangeHandler = (index, value) => {
        let updatedConditions = props.conditions
        updatedConditions[index].value = value
        setConditions(updatedConditions)
        updateConditions(updatedConditions)
    }

    const addConditionButtonClickHandler = () => {
        let updatedConditions = props.conditions
        updatedConditions.push({
        column: "",
        condition: "EQUALS",
        value: ""
        })
        setConditions(updatedConditions)
        updateConditions(updatedConditions)
    }

    const removeConditionButtonClickHandler = (conditionIndex) => {
        let updatedConditions = props.conditions
        updatedConditions = updatedConditions.filter((c, index) => index != conditionIndex)
        setConditions(updatedConditions)
        updateConditions(updatedConditions)
    }

  const updateConditions = (conditions) => {
    props.onUpdateConditions(conditions)
  }

  return (
    <>
    {props.conditions.length > 0 && (
        <Table striped bordered hover>
            <thead>
            <tr>
                <th>#</th>
                <th>Column</th>
                <th>Operator</th>
                <th>Value</th>
                <th></th>
            </tr>
            </thead>
            <tbody>
            {props.conditions.map((condition, conditionIndex) => (
                <tr key={conditionIndex}>
                <td>{conditionIndex + 1}</td>
                <td>
                    <Form.Control value={condition.column} onChange={(e) => txtConditionColumnChangeHandler(conditionIndex, e.target.value)}/>
                </td>
                <td>
                    <Select
                        classNamePrefix="react-select"
                        options={streamConditionOperators}
                        value={streamConditionOperators.find(o => o.value == condition.operator)}
                        onChange={(e) => selectOperatorChangeHandler(conditionIndex, e)}
                        menuPlacement="auto"
                        menuPosition="fixed" />
                </td>
                <td>
                    <Form.Control value={condition.value} onChange={(e) => txtConditionValueChangeHandler(conditionIndex, e.target.value)}/>
                </td>
                <td>
                    <Button variant="danger" 
                        onClick={() => removeConditionButtonClickHandler(conditionIndex)}
                        style={{ height: 46 }}>
                        Remove
                    </Button>
                </td>
                </tr>
            ))}
            </tbody>
        </Table>
    )}
    <Button variant='primary' onClick={addConditionButtonClickHandler}>
        Add Condition
    </Button>
    </>
  )
}

export default StreamConditions