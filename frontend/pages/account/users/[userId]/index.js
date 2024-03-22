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

import Loader from '../../../../assets/icons/loader.svg'

import AccountLayout from '../../../../layouts/account'

import service from '../../../../service'

import accountStyles from "../../../../styles/Account.module.css"

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

  const [userForm, setUserForm] = useState({
    id: 0,
    email: "",
    username: "",
    profile: {
        fullName: "",
        country: "",
        companyName: "",
    },
    submitting: false
  })


  const getUserCountries = () => {
    service.get("/user_countries/", response => {
      setUserCountries(response.data)
    })
  }

  const getUser = () => {
    service.get("/user/", response => {
      setUserForm(
        produce((draft) => {
          draft.id = response.data.id
          draft.email = response.data.email
          draft.username = response.data.username
          draft.profile.fullName = response.data.profile.fullName
          draft.profile.companyName = response.data.profile.companyName
          draft.profile.country = userCountries.find(c => c.value == response.data.profile.country)
        }
      )
    )
    })
  }
  const fullNameChangeHandler = (e) => {
    setProfileForm(
      produce((draft) => {
        draft.profile.fullName = e.target.value
      })
    )
  }

  const companyNameChangeHandler = (e) => {
    setProfileForm(
      produce((draft) => {
        draft.profile.companyName = e.target.value
      })
    )
  }

  const countryChangeHandler = (e) => {
    setProfileForm(
      produce((draft) => {
        draft.profile.country = e
      })
    )
  }

  const resetPasswordBtnClickHandler = (e) => {
    setUserForm(
    produce((draft) => {
        draft.submitting = true
    })
    )
    service.post("/rest-auth/password/reset/", {
        email: userForm.email
    }, response => {
        setUserForm(
            produce((draft) => {
                draft.submitting = false
            })
        )
        setFormSuccessMessage("Reset password email sent.")
    })
  }

  const saveBtnClickHandler = (e) => {
    setUserForm(
      produce((draft) => {
        draft.submitting = true
      })
    )
    service.put("/user/", {
        profile: {
            fullName: profileForm.fullName,
            country: profileForm.country.value,
            companyName: profileForm.companyName,
        }
    }, response => {
        setUserForm(
            produce((draft) => {
                draft.submitting = false
            })
        )
    })
  }

  const backBtnClickHandler = () => {
    router.push("/account/users/")
  }

  useEffect(() => {
    getUserCountries()
  }, [])

  useEffect(() => {
    getUser()
  }, [userCountries])

  return (
    <AccountLayout>
      {userForm?.email != "" && (
        <>
          <h1 className={accountStyles.h1}>User</h1>
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
                    value={userForm.profile.fullName}/>
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
                    value={userForm.profile.country}/>
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
                    value={userForm.profile.companyName}/>
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
                    value={userForm.email} />
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
                    value={userForm.username} />
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
                          style={{ marginRight: 10 }}
                          onClick={(e) => saveBtnClickHandler(e)}
                          disabled={userForm.submitting}>
                            {userForm.submitting && <img className="spinner" src={Loader.src} />}{userForm.submitting ? "Loading": "Save"}</Button>
                    <Button className={accountStyles.resetPasswordBtn + " " + accountStyles.btn}
                          style={{ marginRight: 10 }}
                          onClick={(e) => resetPasswordBtnClickHandler(e)}
                          disabled={userForm.submitting}>
                            {userForm.submitting && <img className="spinner" src={Loader.src} />}{userForm.submitting ? "Loading": "Reset Password"}</Button>
                    <Button variant="secondary" onClick={backBtnClickHandler}>
                        Back
                    </Button>
                </Form.Group>
              </Row>
            </Form>
          </div>
        </>
      )}
    </AccountLayout>
  )
}
