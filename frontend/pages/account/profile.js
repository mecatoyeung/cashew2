import { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { useRouter } from 'next/router'
import Image from 'next/image'

import { produce } from 'immer'

import { Form } from 'react-bootstrap'
import { Modal } from 'react-bootstrap'
import { Button } from 'react-bootstrap'
import { Dropdown } from 'react-bootstrap'
import { Row, Col } from 'react-bootstrap'

import Select from 'react-select'

import AccountLayout from '../../layouts/account'

import service from '../../service'

import accountStyles from "../../styles/Account.module.css"

export default function Profile() {

  const router = useRouter()

  const { } = router.query

  const [userCountries, setUserCountries] = useState([])

  const [formSuccessMessage, setFormSuccessMessage] = useState("")
  const [formErrorMessages, setFormErrorMessages] = useState(null)

  const [formValidation, setFormValidation] = useState({
    isValid: true,
    errorMessages: {
      fullName: "",
      country: "",
      companyName: ""
    }
  })

  const getUserCountries = () => {
    service.get("/user_countries/", response => {
      setUserCountries(response.data)
    })
  }

  const getProfile = () => {
    service.get("/profiles/", response => {
      setProfileForm(
        produce((draft) => {
          draft.fullName = response.data[0].fullName
          draft.companyName = response.data[0].companyName
          draft.country = userCountries.find(c => c.value == response.data[0].country)
          draft.user.id = response.data[0].user.id
          draft.user.email = response.data[0].user.email
          draft.user.username = response.data[0].user.username
        }
      )
    )
    })
  }

  const [profileForm, setProfileForm] = useState({
    fullName: "",
    country: "",
    companyName: "",
    user: {
        id: 0,
        email: "",
        username: ""
    },
    submitting: false
  })

  const fullNameChangeHandler = (e) => {
    setProfileForm(
      produce((draft) => {
        draft.fullName = e.target.value
      })
    )
  }

  const companyNameChangeHandler = (e) => {
    setProfileForm(
      produce((draft) => {
        draft.companyName = e.target.value
      })
    )
  }

  const countryChangeHandler = (e) => {
    setProfileForm(
      produce((draft) => {
        draft.country = e
      })
    )
  }

  const saveBtnClickHandler = (e) => {
    service.put("/profiles/" + profileForm.user.id, {
        fullName: profileForm.fullName,
        country: profileForm.country.value,
        companyName: profileForm.companyName,
    })
  }

  useEffect(() => {
    getUserCountries()
  }, [])

  useEffect(() => {
    getProfile()
  }, [userCountries])

  return (
    <AccountLayout>
        <h1 className={accountStyles.h1}>Profile</h1>
        <div className={accountStyles.profileDiv}>
            <Form>
              <Row>
                <Form.Group as={Col} className={accountStyles.col + " xs-12" + " md-3"} controlId="formFullName">
                  <Form.Label>Full Name</Form.Label>
                  <Form.Control
                    type="text"
                    name="fullName"
                    placeholder="Enter full name"
                    onChange={(e) => fullNameChangeHandler(e)}
                    value={profileForm.fullName}/>
                    {!formValidation.isValid && (
                      <div className="formErrorMessage">
                        {formValidation.errorMessages.fullName}
                      </div>
                    )}
                </Form.Group>
              </Row>
              <Row>
                <Form.Group as={Col} className={accountStyles.col + " xs-12" + " md-3"} controlId="formCountry">
                  <Form.Label>Country</Form.Label>
                  <Select 
                    instanceId="userCountriesSelectId" 
                    options={userCountries} 
                    onChange={countryChangeHandler}
                    value={profileForm.country}/>
                </Form.Group>
              </Row>
              <Row>
                <Form.Group as={Col} className={accountStyles.col + " xs-12" + " md-3"} controlId="formCompanyName">
                  <Form.Label>Company Name</Form.Label>
                  <Form.Control
                    type="text"
                    name="companyName"
                    placeholder="Enter company name"
                    onChange={(e) => companyNameChangeHandler(e)}
                    value={profileForm.companyName}/>
                    {!formValidation.isValid && (
                      <div className="formErrorMessage">
                        {formValidation.errorMessages.companyName}
                      </div>
                    )}
                </Form.Group>
              </Row>
              <Row>
                <Form.Group as={Col} className={accountStyles.col + " xs-12" + " md-3"} controlId="formEmail">
                  <Form.Label>Email</Form.Label>
                  <Form.Control
                    type="email"
                    name="email"
                    placeholder="Enter email"
                    autoComplete="email"
                    disabled
                    value={profileForm.user.email} />
                  {!formValidation.isValid && (
                      <div className="formErrorMessage">
                        {formValidation.errorMessages.email}
                      </div>
                    )}
                </Form.Group>
              </Row>
              <Row>
                <Form.Group as={Col} className={accountStyles.col + " xs-12" + " md-3"} controlId="formUsername">
                  <Form.Label>Username</Form.Label>
                  <Form.Control
                    type="text"
                    name="username"
                    placeholder="Enter username"
                    autoComplete="username"
                    disabled
                    value={profileForm.user.username} />
                  {!formValidation.isValid && (
                      <div className="formErrorMessage">
                        {formValidation.errorMessages.username}
                      </div>
                    )}
                </Form.Group>
              </Row>
              {formSuccessMessage && formSuccessMessage.length > 0 && (
                <Row>
                  <div className="formSuccessMessage">
                    {formSuccessMessage}
                  </div>
                </Row>
              )}
              <Row>
              {formErrorMessages && Object.keys(formErrorMessages).length > 0 && Object.keys(formErrorMessages).map(function(key, index) {
                return formErrorMessages[key].map(message => {
                  return (
                    <div className="formErrorMessage" key={message}>
                      {message}
                    </div>
                  )
                })
              })}
              </Row>
              <Row>
                <Form.Group as={Col} className={accountStyles.actions + " " + accountStyles.col + " xs-12" + " md-3"}>
                  <Button className={accountStyles.saveBtn + " " + accountStyles.btn}
                          onClick={(e) => saveBtnClickHandler(e)}
                          disabled={profileForm.submitting}>
                            {profileForm.submitting && <img className="spinner" src={Loader.src} />}{profileForm.submitting ? "Loading": "Save"}</Button>
                </Form.Group>
              </Row>
            </Form>
        </div>
    </AccountLayout>
  )
}
