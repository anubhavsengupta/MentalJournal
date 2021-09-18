from flask import Flask, redirect, url_for, render_template, request, session, flash
import secrets
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
